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

//! `aflags` is a device binary to read and write aconfig flags.

use anyhow::{anyhow, Result};
use clap::Parser;

mod device_config_source;
use device_config_source::DeviceConfigSource;

#[derive(Clone)]
enum FlagPermission {
    ReadOnly,
    ReadWrite,
}

impl ToString for FlagPermission {
    fn to_string(&self) -> String {
        match &self {
            Self::ReadOnly => "read-only".into(),
            Self::ReadWrite => "read-write".into(),
        }
    }
}

#[derive(Clone)]
enum OverrideType {
    Default_,
    Server,
}

impl ToString for OverrideType {
    fn to_string(&self) -> String {
        match &self {
            Self::Default_ => "default".into(),
            Self::Server => "server".into(),
        }
    }
}

#[derive(Clone)]
struct Flag {
    namespace: String,
    name: String,
    package: String,
    container: String,
    value: String,
    permission: FlagPermission,
    override_type: OverrideType,
}

trait FlagSource {
    fn list_flags() -> Result<Vec<Flag>>;
    fn override_flag(namespace: &str, package: &str, name: &str, value: &str) -> Result<()>;
}

const ABOUT_TEXT: &str = "Tool for reading and writing flags.

Rows in the table from the `list` command follow this format:

  package flag_name value provenance permission container

  * `package`: package set for this flag in its .aconfig definition.
  * `flag_name`: flag name, also set in definition.
  * `value`: the value read from the flag.
  * `provenance`: one of:
    + `default`: the flag value comes from its build-time default.
    + `manual`: the flag value comes from a local manual override.
    + `server`: the flag value comes from a server override.
  * `permission`: read-write or read-only.
  * `container`: the container for the flag, configured in its definition.
";

#[derive(Parser, Debug)]
#[clap(long_about=ABOUT_TEXT)]
struct Cli {
    #[clap(subcommand)]
    command: Command,
}

#[derive(Parser, Debug)]
enum Command {
    /// List all aconfig flags on this device.
    List,

    /// Enable an aconfig flag on this device, on the next boot.
    Enable { package: String, name: String },

    /// Disable an aconfig flag on this device, on the next boot.
    Disable { package: String, name: String },
}

struct PaddingInfo {
    longest_package_col: usize,
    longest_name_col: usize,
    longest_val_col: usize,
    longest_override_type_col: usize,
    longest_permission_col: usize,
}

fn format_flag_row(flag: &Flag, info: &PaddingInfo) -> String {
    let pkg = &flag.package;
    let p0 = info.longest_package_col + 1;

    let name = &flag.name;
    let p1 = info.longest_name_col + 1;

    let val = flag.value.to_string();
    let p2 = info.longest_val_col + 1;

    let override_type = flag.override_type.to_string();
    let p3 = info.longest_override_type_col + 1;

    let perm = flag.permission.to_string();
    let p4 = info.longest_permission_col + 1;

    let container = &flag.container;

    format!("{pkg:p0$}{name:p1$}{val:p2$}{override_type:p3$}{perm:p4$}{container}\n")
}

fn set_flag(package: &str, name: &str, value: &str) -> Result<String> {
    let flags_binding = DeviceConfigSource::list_flags()?;
    let flag =
        flags_binding.iter().find(|f| f.name == name && f.package == package).ok_or(anyhow!(
            "no aconfig flag '{}/{}'. Does the flag have an .aconfig definition?",
            package,
            name
        ))?;

    if let FlagPermission::ReadOnly = flag.permission {
        return Err(anyhow!(
            "could not write flag '{}/{}', it is read-only for the current release configuration.",
            package,
            name
        ));
    }

    DeviceConfigSource::override_flag(&flag.namespace, package, name, value)?;

    let status_display = match value {
        "true" => "enabled",
        "false" => "disabled",
        _ => return Err(anyhow!("unsupported override type {}", value)),
    };

    Ok(format!(
        "Successfully {} flag {}/{}. Reboot the device to apply the change.",
        status_display, package, name
    ))
}

fn list() -> Result<String> {
    let flags = DeviceConfigSource::list_flags()?;
    let padding_info = PaddingInfo {
        longest_package_col: flags.iter().map(|f| f.package.len()).max().unwrap_or(0),
        longest_name_col: flags.iter().map(|f| f.name.len()).max().unwrap_or(0),
        longest_val_col: flags.iter().map(|f| f.value.to_string().len()).max().unwrap_or(0),
        longest_override_type_col: flags
            .iter()
            .map(|f| f.override_type.to_string().len())
            .max()
            .unwrap_or(0),
        longest_permission_col: flags
            .iter()
            .map(|f| f.permission.to_string().len())
            .max()
            .unwrap_or(0),
    };

    let mut result = String::from("");
    for flag in flags {
        let row = format_flag_row(&flag, &padding_info);
        result.push_str(&row);
    }
    Ok(result)
}

fn main() {
    let cli = Cli::parse();
    let output = match cli.command {
        Command::List => list(),
        Command::Enable { package, name } => set_flag(&package, &name, "true"),
        Command::Disable { package, name } => set_flag(&package, &name, "false"),
    };
    match output {
        Ok(text) => println!("{text}"),
        Err(msg) => println!("Error: {}", msg),
    }
}
