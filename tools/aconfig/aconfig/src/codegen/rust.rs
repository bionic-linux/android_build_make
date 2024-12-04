/*
 * Copyright (C) 2023 The Android Open Source Project
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

use anyhow::Result;
use serde::Serialize;
use tinytemplate::TinyTemplate;

use aconfig_protos::{ProtoFlagPermission, ProtoFlagState, ProtoParsedFlag};

use std::collections::HashMap;

use crate::codegen;
use crate::codegen::CodegenMode;
use crate::commands::OutputFile;

pub fn generate_rust_code<I>(
    package: &str,
    flag_ids: HashMap<String, u16>,
    parsed_flags_iter: I,
    codegen_mode: CodegenMode,
    allow_instrumentation: bool,
    enable_fingerprint: bool,
    fingerprint_value: u64,
) -> Result<OutputFile>
where
    I: Iterator<Item = ProtoParsedFlag>,
{
    let template_flags: Vec<TemplateParsedFlag> = parsed_flags_iter
        .map(|pf| TemplateParsedFlag::new(package, flag_ids.clone(), &pf))
        .collect();
    let has_readwrite = template_flags.iter().any(|item| item.readwrite);
    let container = (template_flags.first().expect("zero template flags").container).to_string();
    let context = TemplateContext {
        package: package.to_string(),
        template_flags,
        modules: package.split('.').map(|s| s.to_string()).collect::<Vec<_>>(),
        has_readwrite,
        allow_instrumentation,
        container,
        enable_fingerprint,
        fingerprint_value,
    };
    let mut template = TinyTemplate::new();
    template.add_template(
        "rust_code_gen",
        match codegen_mode {
            CodegenMode::Test => include_str!("../../templates/rust_test.template"),
            CodegenMode::Exported | CodegenMode::ForceReadOnly | CodegenMode::Production => {
                include_str!("../../templates/rust.template")
            }
        },
    )?;
    let contents = template.render("rust_code_gen", &context)?;
    let path = ["src", "lib.rs"].iter().collect();
    Ok(OutputFile { contents: contents.into(), path })
}

#[derive(Serialize)]
struct TemplateContext {
    pub package: String,
    pub template_flags: Vec<TemplateParsedFlag>,
    pub modules: Vec<String>,
    pub has_readwrite: bool,
    pub allow_instrumentation: bool,
    pub container: String,
    pub enable_fingerprint: bool,
    pub fingerprint_value: u64, // Will be ignored if enable_fingerprint is false.
}

#[derive(Serialize)]
struct TemplateParsedFlag {
    pub readwrite: bool,
    pub default_value: String,
    pub name: String,
    pub container: String,
    pub flag_offset: u16,
    pub device_config_namespace: String,
    pub device_config_flag: String,
}

impl TemplateParsedFlag {
    #[allow(clippy::nonminimal_bool)]
    fn new(package: &str, flag_offsets: HashMap<String, u16>, pf: &ProtoParsedFlag) -> Self {
        let no_assigned_offset = (pf.container() == "system"
            || pf.container() == "vendor"
            || pf.container() == "product")
            && pf.permission() == ProtoFlagPermission::READ_ONLY
            && pf.state() == ProtoFlagState::DISABLED;

        let flag_offset = match flag_offsets.get(pf.name()) {
            Some(offset) => offset,
            None => {
                // System/vendor/product RO+disabled flags have no offset in storage files.
                // Assign placeholder value.
                if no_assigned_offset {
                    &0
                }
                // All other flags _must_ have an offset.
                else {
                    panic!("{}", format!("missing flag offset for {}", pf.name()));
                }
            }
        };

        Self {
            readwrite: pf.permission() == ProtoFlagPermission::READ_WRITE,
            default_value: match pf.state() {
                ProtoFlagState::ENABLED => "true".to_string(),
                ProtoFlagState::DISABLED => "false".to_string(),
            },
            name: pf.name().to_string(),
            container: pf.container().to_string(),
            flag_offset: *flag_offset,
            device_config_namespace: pf.namespace().to_string(),
            device_config_flag: codegen::create_device_config_ident(package, pf.name())
                .expect("values checked at flag parse time"),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    use crate::commands::assign_flag_ids;

    fn test_generate_rust_code(
        mode: CodegenMode,
        allow_instrumentation: bool,
        fingerprint_enabled: bool,
        expected: &str,
    ) {
        let parsed_flags = crate::test::parse_test_flags();
        let modified_parsed_flags =
            crate::commands::modify_parsed_flags_based_on_mode(parsed_flags, mode).unwrap();
        let flag_ids =
            assign_flag_ids(crate::test::TEST_PACKAGE, modified_parsed_flags.iter()).unwrap();
        let generated = generate_rust_code(
            crate::test::TEST_PACKAGE,
            flag_ids,
            modified_parsed_flags.into_iter(),
            mode,
            allow_instrumentation,
            fingerprint_enabled,
            8u64, // Random fingerprint value used in testing.
        )
        .unwrap();
        assert_eq!("src/lib.rs", format!("{}", generated.path.display()));
        assert_eq!(
            None,
            crate::test::first_significant_code_diff(
                expected,
                &String::from_utf8(generated.contents).unwrap()
            )
        );
    }

    #[test]
    fn test_generate_rust_code_for_prod() {
        let expected = include_str!("testdata/rust/rust_prod_expected.txt");
        test_generate_rust_code(CodegenMode::Production, false, false, expected);
    }

    #[test]
    fn test_generate_rust_code_for_prod_instrumented() {
        let expected = include_str!("testdata/rust/rust_prod_instrumented_expected.txt");
        test_generate_rust_code(CodegenMode::Production, true, false, expected);
    }

    #[test]
    fn test_generate_rust_code_for_test() {
        let expected = include_str!("testdata/rust/rust_test_expected.txt");
        test_generate_rust_code(CodegenMode::Test, false, false, expected);
    }

    #[test]
    fn test_generate_rust_code_for_exported() {
        let expected = include_str!("testdata/rust/rust_exported_expected.txt");
        test_generate_rust_code(CodegenMode::Exported, false, false, expected);
    }

    #[test]
    fn test_generate_rust_code_for_force_read_only() {
        let expected = include_str!("testdata/rust/rust_forced_read_only_expected.txt");
        test_generate_rust_code(CodegenMode::ForceReadOnly, false, false, expected);
    }

    #[test]
    fn test_generate_rust_code_no_fingerprint_match() {
        let expected = include_str!("testdata/rust/rust_fingerprint_enabled_expected.txt");
        test_generate_rust_code(CodegenMode::Production, true, true, expected);
    }
}
