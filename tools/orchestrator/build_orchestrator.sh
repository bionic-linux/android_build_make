#!/bin/bash
set -euo pipefail

# Copyright (C) 2022 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Skeleton of the multi-tree build orchestrator
# Individual subcomponents will be implemented over time


# Step 1: Parse the new lunch file
# Input: TARGET_BUILD_COMBO
# Output: [(inner_tree,TARGET_PRODUCT)...]
# Hardcode system_inner_tree to ANDROID_BUILD_TOP for now
system_inner_tree="$ANDROID_BUILD_TOP"

# Step 2: Parse the outertree manifest file to create nsjail config
# This is necessary for mounting shared code inner trees


# Step 3: Build the API surfaces (CC+Java) per inner tree
# TODO(spandandas): This might run in multi-tree nsjail

# Build the api surfaces using bazel. This action creates json files in the
# bazel out directory
# Arguments:
#   $1: inner_tree to step into
#   $2-n: bazel targets
# Outputs:
#   None
function build_api_surfaces_using_bazel(){
  inner_tree="$1"
  shift;
  # Use prebuilt bazel directly instead of the bazel() function added by
  # build/make/envsetup.sh
  # The shell function runs the prebuilt bazel using --config=bp2build|queryview, and
  # depends on values generated from Soong
  # The api surfaces do not have any dependencies on Soong, and therefore can be
  # built/queried in standalone/pure mode
  (cd "$inner_tree" && prebuilts/bazel/linux-x86_64/bazel build $@)
}
# TODO(spandandas): Update the lists
SYSTEM_JAVA_API_SURFACES=
SYSTEM_CC_API_SURFACES=${SYSTEM_CC_API_SURFACES:=//build/bazel/tests/api_surface:ndk}
build_api_surfaces_using_bazel "$system_inner_tree" "$SYSTEM_JAVA_API_SURFACES" "$SYSTEM_CC_API_SURFACES"
# TODO(spandandas): Build api surfaces from mainline modules

# Step 4: Copy the API surface contribution files to multi-tree out
# TODO(spandandas): Write to single tree out directory for now
OUT_DIR=${OUT_DIR:="$ANDROID_BUILD_TOP"/out/api_surfaces}
OUT_DIR_CC="$OUT_DIR"/cc
for cc_api_surface in $SYSTEM_CC_API_SURFACES; do
  $(dirname "$0")/gen_cc_api_surface.sh "$OUT_DIR_CC" "$cc_api_surface" "$system_inner_tree"
done
# TODO(spandandas): java api surfaces and mainline modules

# Step 5: Mount Generated API surfaces to compile API domains (m nothing)
# Each inner tree outputs a ninja file


# Step 6: Create ninja rules to copy apexes between inner trees
# This step is a function of TARGET_BUILD_COMBO


# Step 7: Run ninja in multi-tree nsjail
