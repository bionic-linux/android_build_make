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

//! `aconfig-storage` is a debugging tool to parse storage files

use aconfig_storage_file::{
    list_flags, read_file_to_bytes, AconfigStorageError, FlagInfoList, FlagTable, FlagValueList,
    PackageTable, StorageFileType,
};

use clap::{builder::ArgAction, Arg, Command};

fn cli() -> Command {
    Command::new("aconfig-storage")
        .subcommand_required(true)
        .subcommand(
            Command::new("print")
                .arg(Arg::new("file").long("file").required(true).action(ArgAction::Set))
                .arg(
                    Arg::new("type")
                        .long("type")
                        .required(true)
                        .value_parser(|s: &str| StorageFileType::try_from(s)),
                ),
        )
        .subcommand(
            Command::new("list")
                .arg(
                    Arg::new("package-map")
                        .long("package-map")
                        .required(true)
                        .action(ArgAction::Set),
                )
                .arg(Arg::new("flag-map").long("flag-map").required(true).action(ArgAction::Set))
                .arg(Arg::new("flag-val").long("flag-val").required(true).action(ArgAction::Set)),
        )
}

fn print_storage_file(
    file_path: &str,
    file_type: &StorageFileType,
) -> Result<(), AconfigStorageError> {
    let bytes = read_file_to_bytes(file_path)?;
    match file_type {
        StorageFileType::PackageMap => {
            let package_table = PackageTable::from_bytes(&bytes)?;
            println!("{:?}", package_table);
        }
        StorageFileType::FlagMap => {
            let flag_table = FlagTable::from_bytes(&bytes)?;
            println!("{:?}", flag_table);
        }
        StorageFileType::FlagVal => {
            let flag_value = FlagValueList::from_bytes(&bytes)?;
            println!("{:?}", flag_value);
        }
        StorageFileType::FlagInfo => {
            let flag_info = FlagInfoList::from_bytes(&bytes)?;
            println!("{:?}", flag_info);
        }
    }
    Ok(())
}

fn main() -> Result<(), AconfigStorageError> {
    let matches = cli().get_matches();
    match matches.subcommand() {
        Some(("print", sub_matches)) => {
            let file_path = sub_matches.get_one::<String>("file").unwrap();
            let file_type = sub_matches.get_one::<StorageFileType>("type").unwrap();
            print_storage_file(file_path, file_type)?
        }
        Some(("list", sub_matches)) => {
            let package_map = sub_matches.get_one::<String>("package-map").unwrap();
            let flag_map = sub_matches.get_one::<String>("flag-map").unwrap();
            let flag_val = sub_matches.get_one::<String>("flag-val").unwrap();
            let flags = list_flags(package_map, flag_map, flag_val)?;
            for (package_name, flag_name, flag_type, flag_value) in flags.iter() {
                println!("{} {} {:?} {}", package_name, flag_name, flag_type, flag_value);
            }
        }
        _ => unreachable!(),
    }
    Ok(())
}
