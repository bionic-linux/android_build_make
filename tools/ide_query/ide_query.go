/*
 * Copyright (C) 2024 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// Binary ide_query generates and analyzes build artifacts.
// The produced result can be consumed by IDEs to provide language features.
package main

import (
	"bytes"
	"container/list"
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"os"
	"os/exec"
	"path"
	"slices"
	"strings"

	"google.golang.org/protobuf/proto"
	pb "ide_query/ide_query_proto"
)

// Env contains information about the current environment.
type Env struct {
	LunchTarget             LunchTarget
	RepoDir                 string
	OutDir                  string
	PrebuiltsClangToolsRoot string

	CcFiles []string

	JavaFiles           []string
	JavaModules         map[string]*javaModule // mapping from module name to module
	JavaFileToModuleMap map[string]*javaModule // mapping from file path to module
}

// LunchTarget is a parsed Android lunch target.
// Input format: <product_name>-<release_type>-<build_variant>
type LunchTarget struct {
	Product string
	Release string
	Variant string
}

var _ flag.Value = (*LunchTarget)(nil)

// // Get implements flag.Value.
// func (l *LunchTarget) Get() any {
// 	return l
// }

// Set implements flag.Value.
func (l *LunchTarget) Set(s string) error {
	parts := strings.Split(s, "-")
	if len(parts) != 3 {
		return fmt.Errorf("invalid lunch target: %q, must have form <product_name>-<release_type>-<build_variant>", s)
	}
	*l = LunchTarget{
		Product: parts[0],
		Release: parts[1],
		Variant: parts[2],
	}
	return nil
}

// String implements flag.Value.
func (l *LunchTarget) String() string {
	return fmt.Sprintf("%s-%s-%s", l.Product, l.Release, l.Variant)
}

func RepoState(env *Env) pb.RepoState {
	const compDbPath = "soong/development/ide/compdb/compile_commands.json"
	return pb.RepoState{
		RepoDir:        env.RepoDir,
		ActiveFilePath: env.CcFiles,
		OutDir:         env.OutDir,
		CompDbPath:     path.Join(env.OutDir, compDbPath),
	}
}

func RunCCanalyzer(ctx context.Context, env *Env, mode string, in []byte) []byte {
	ccAnalyzerPath := path.Join(env.PrebuiltsClangToolsRoot, "bin/ide_query_cc_analyzer")
	outBuffer := bytes.Buffer{}

	inBuffer := bytes.Buffer{}
	inBuffer.Write(in)

	cmd := exec.CommandContext(ctx, ccAnalyzerPath, "--mode="+mode)
	cmd.Dir = env.RepoDir

	cmd.Stdin = &inBuffer
	cmd.Stdout = &outBuffer
	cmd.Stderr = os.Stderr

	if err := cmd.Run(); err != nil {
		log.Fatal(err)
	}

	return outBuffer.Bytes()
}

// Execute cc_analyzer and get all the targets that needs to be build for analyzing files.
func GetCCTargets(ctx context.Context, env *Env) ([]string, pb.Status) {
	state := RepoState(env)
	bytes, err := proto.Marshal(&state)
	if err != nil {
		log.Fatalln("Failed to serialize state:", err)
	}

	resp := pb.DepsResponse{}
	proto.Unmarshal(RunCCanalyzer(ctx, env, "deps", bytes), &resp)

	var targets []string
	if resp.Status != nil && resp.Status.Code != pb.Status_OK {
		return targets, *resp.Status
	}
	for _, deps := range resp.Deps {
		targets = append(targets, deps.BuildTarget...)
	}
	return targets, pb.Status{Code: pb.Status_OK}
}

func GetCCInputs(ctx context.Context, env *Env) pb.IdeAnalysis {
	state := RepoState(env)
	bytes, err := proto.Marshal(&state)
	if err != nil {
		log.Fatalln("Failed to serialize state:", err)
	}

	resp := pb.IdeAnalysis{}
	proto.Unmarshal(RunCCanalyzer(ctx, env, "inputs", bytes), &resp)
	return resp
}

func JavaFileToModuleMaps(ctx context.Context, env *Env) map[string]*javaModule {
	fileToModule := make(map[string]*javaModule) // file path -> module
	for _, f := range env.JavaFiles {
		for _, m := range env.JavaModules {
			if !slices.Contains(m.Srcs, f) {
				continue
			}
			if fileToModule[f] != nil {
				// TODO(michaelmerg): Handle the case where a file is covered by multiple modules.
				log.Printf("File %q found in module %q but is already covered by module %q", f, m.Name, fileToModule[f].Name)
				continue
			}
			fileToModule[f] = m
		}
	}
	return fileToModule
}

func GetJavaTargets(ctx context.Context, env *Env) []string {
	var targets []string
	for _, m := range env.JavaFileToModuleMap {
		targets = append(targets, m.Name)
	}
	return targets
}

func GetJavaInputs(ctx context.Context, env *Env) pb.IdeAnalysis {
	var sources []*pb.SourceFile
	type depsAndGenerated struct {
		Deps      []string
		Generated []*pb.GeneratedFile
	}
	moduleToDeps := make(map[string]*depsAndGenerated)
	for _, f := range env.JavaFiles {
		file := &pb.SourceFile{
			Path: f,
		}
		sources = append(sources, file)

		m := env.JavaFileToModuleMap[f]
		if m == nil {
			file.Status = &pb.Status{
				Code:    pb.Status_FAILURE,
				Message: proto.String("File not found in any module."),
			}
			continue
		}

		file.Status = &pb.Status{Code: pb.Status_OK}
		if moduleToDeps[m.Name] != nil {
			file.Generated = moduleToDeps[m.Name].Generated
			file.Deps = moduleToDeps[m.Name].Deps
			continue
		}

		deps := transitiveDeps(m, env.JavaModules)
		var generated []*pb.GeneratedFile
		outPrefix := env.OutDir + "/"
		for _, d := range deps {
			if relPath, ok := strings.CutPrefix(d, outPrefix); ok {
				contents, err := os.ReadFile(d)
				if err != nil {
					fmt.Printf("Generated file %q not found - will be skipped.\n", d)
					continue
				}

				generated = append(generated, &pb.GeneratedFile{
					Path:     relPath,
					Contents: contents,
				})
			}
		}
		moduleToDeps[m.Name] = &depsAndGenerated{deps, generated}
		file.Generated = generated
		file.Deps = deps
	}
	return pb.IdeAnalysis{
		Sources: sources,
	}
}

func main() {
	var env Env
	env.OutDir = os.Getenv("OUT_DIR")
	env.RepoDir = os.Getenv("ANDROID_BUILD_TOP")
	env.PrebuiltsClangToolsRoot = os.Getenv("PREBUILTS_CLANG_TOOLS_ROOT")
	flag.Var(&env.LunchTarget, "lunch_target", "The lunch target to query")
	flag.Parse()
	files := flag.Args()
	if len(files) == 0 {
		fmt.Println("No files provided.")
		os.Exit(1)
		return
	}

	for _, f := range files {
		switch {
		case strings.HasSuffix(f, ".java") || strings.HasSuffix(f, ".kt"):
			env.JavaFiles = append(env.JavaFiles, f)
		case strings.HasSuffix(f, ".cc") || strings.HasSuffix(f, ".cpp") || strings.HasSuffix(f, ".h"):
			env.CcFiles = append(env.CcFiles, f)
		default:
			log.Printf("File %q is supported - will be skipped.", f)
		}
	}

	ctx := context.Background()
	// TODO(michaelmerg): Figure out if module_bp_java_deps.json and compile_commands.json is outdated.
	runMake(ctx, env, "nothing")

	if err := env.loadJavaModules(); err != nil {
		log.Printf("Failed to load java modules: %v", err)
	}
	toMake := GetJavaTargets(ctx, &env)

	ccTargets, status := GetCCTargets(ctx, &env)
	if status.Code != pb.Status_OK {
		log.Fatalf("Failed to query cc targets: %v", *status.Message)
	}
	toMake = append(toMake, ccTargets...)
	fmt.Printf("Running make for modules: %v\n", strings.Join(toMake, ", "))
	if err := runMake(ctx, env, toMake...); err != nil {
		log.Printf("Building deps failed: %v", err)
	}

	res := GetJavaInputs(ctx, &env)
	ccAnalysis := GetCCInputs(ctx, &env)
	proto.Merge(&res, &ccAnalysis)

	res.BuildArtifactRoot = env.OutDir
	data, err := proto.Marshal(&res)
	if err != nil {
		log.Fatalf("Failed to marshal result proto: %v", err)
	}

	err = os.WriteFile(path.Join(env.RepoDir, env.OutDir, "ide_query.pb"), data, 0644)
	if err != nil {
		log.Fatalf("Failed to write result proto: %v", err)
	}

	for _, s := range res.Sources {
		fmt.Printf("%s: %v (Deps: %d, Generated: %d)\n", s.GetPath(), s.GetStatus(), len(s.GetDeps()), len(s.GetGenerated()))
	}
}

// runMake runs Soong build for the given modules.
func runMake(ctx context.Context, env Env, modules ...string) error {
	args := []string{
		"--make-mode",
		"ALLOW_UNKNOWN_WARNING_OPTION=1",
		"SOONG_GEN_COMPDB=1",
		"ANDROID_BUILD_ENVIRONMENT_CONFIG=googler-cog",
		"TARGET_PRODUCT=" + env.LunchTarget.Product,
		"TARGET_RELEASE=" + env.LunchTarget.Release,
		"TARGET_BUILD_VARIANT=" + env.LunchTarget.Variant,
	}
	args = append(args, modules...)
	cmd := exec.CommandContext(ctx, "build/soong/soong_ui.bash", args...)
	cmd.Dir = env.RepoDir
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	return cmd.Run()
}

type javaModule struct {
	Name    string
	Path    []string `json:"path,omitempty"`
	Deps    []string `json:"dependencies,omitempty"`
	Srcs    []string `json:"srcs,omitempty"`
	Jars    []string `json:"jars,omitempty"`
	SrcJars []string `json:"srcjars,omitempty"`
}

func (env *Env) loadJavaModules() error {
	javaDepsPath := path.Join(env.RepoDir, env.OutDir, "soong/module_bp_java_deps.json")
	data, err := os.ReadFile(javaDepsPath)
	if err != nil {
		return err
	}

	var moduleMapping map[string]*javaModule // module name -> module
	if err = json.Unmarshal(data, &moduleMapping); err != nil {
		return err
	}

	env.JavaModules = make(map[string]*javaModule)
	env.JavaFileToModuleMap = make(map[string]*javaModule)
	for name, module := range moduleMapping {
		if strings.HasSuffix(name, "-jarjar") || strings.HasSuffix(name, ".impl") {
			continue
		}
		module.Name = name
		env.JavaModules[name] = module
		for _, src := range module.Srcs {
			if !slices.Contains(env.JavaFiles, src) {
				// We are only interested in active files.
				continue
			}
			if env.JavaFileToModuleMap[src] != nil {
				// TODO(michaelmerg): Handle the case where a file is covered by multiple modules.
				log.Printf("File %q found in module %q but is already covered by module %q", src, module.Name, env.JavaFileToModuleMap[src].Name)
				continue
			}
			env.JavaFileToModuleMap[src] = module
		}
	}
	return nil
}

func transitiveDeps(m *javaModule, modules map[string]*javaModule) []string {
	var ret []string
	q := list.New()
	q.PushBack(m.Name)
	seen := make(map[string]bool) // module names -> true
	for q.Len() > 0 {
		name := q.Remove(q.Front()).(string)
		mod := modules[name]
		if mod == nil {
			continue
		}

		ret = append(ret, mod.Srcs...)
		ret = append(ret, mod.SrcJars...)
		ret = append(ret, mod.Jars...)
		for _, d := range mod.Deps {
			if seen[d] {
				continue
			}
			seen[d] = true
			q.PushBack(d)
		}
	}
	slices.Sort(ret)
	ret = slices.Compact(ret)
	return ret
}
