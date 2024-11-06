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

// When building with the Android tool-chain
//
//   - an external crate `aconfig_storage_metadata_protos` will be generated
//   - the feature "cargo" will be disabled
//
// When building with cargo
//
//   - a local sub-module will be generated in OUT_DIR and included in this file
//   - the feature "cargo" will be enabled
//
// This module hides these differences from the rest of the codebase.

// ---- When building with the Android tool-chain ----
#[cfg(not(feature = "cargo"))]
mod auto_generated {
    pub use aconfig_storage_protos::aconfig_storage_metadata as ProtoStorage;
    pub use ProtoStorage::Storage_file_info as ProtoStorageFileInfo;
    pub use ProtoStorage::Storage_files as ProtoStorageFiles;
}

// ---- When building with cargo ----
#[cfg(feature = "cargo")]
mod auto_generated {
    // include! statements should be avoided (because they import file contents verbatim), but
    // because this is only used during local development, and only if using cargo instead of the
    // Android tool-chain, we allow it
    include!(concat!(env!("OUT_DIR"), "/aconfig_storage_protos/mod.rs"));
    pub use aconfig_storage_metadata::Storage_file_info as ProtoStorageFileInfo;
    pub use aconfig_storage_metadata::Storage_files as ProtoStorageFiles;
}

// ---- Common for both the Android tool-chain and cargo ----
pub use auto_generated::*;

use protobuf::Message;
use std::io::Write;
use tempfile::NamedTempFile;

pub mod storage_record_pb {
    use std::io;

    use super::*;
    use thiserror::Error;

    #[derive(Debug, Error)]
    pub enum StorageProtoError {
        #[error("Invalid storage file record: missing package map file for container {container}")]
        MissingPackageMap { container: String },
        #[error("Invalid storage file record: missing flag map file for container {container}")]
        MissingFlagMap { container: String },
        #[error("Invalid storage file record: missing flag value file for container {container}")]
        MissingFlagValue { container: String },
        #[error(transparent)]
        Proto(#[from] protobuf::Error),
        #[error(transparent)]
        ProtoParse(#[from] protobuf::text_format::ParseError),
        #[error(transparent)]
        Io(#[from] io::Error),
    }

    pub fn try_from_binary_proto(bytes: &[u8]) -> Result<ProtoStorageFiles, StorageProtoError> {
        let message: ProtoStorageFiles = protobuf::Message::parse_from_bytes(bytes)?;
        verify_fields(&message)?;
        Ok(message)
    }

    pub fn verify_fields(storage_files: &ProtoStorageFiles) -> Result<(), StorageProtoError> {
        for storage_file_info in storage_files.files.iter() {
            if storage_file_info.package_map().is_empty() {
                return Err(StorageProtoError::MissingPackageMap {
                    container: storage_file_info.container().to_owned(),
                });
            }
            if storage_file_info.flag_map().is_empty() {
                return Err(StorageProtoError::MissingFlagMap {
                    container: storage_file_info.container().to_owned(),
                });
            }
            if storage_file_info.flag_val().is_empty() {
                return Err(StorageProtoError::MissingFlagValue {
                    container: storage_file_info.container().to_owned(),
                });
            }
        }
        Ok(())
    }

    pub fn get_binary_proto_from_text_proto(
        text_proto: &str,
    ) -> Result<Vec<u8>, StorageProtoError> {
        let storage_files: ProtoStorageFiles = protobuf::text_format::parse_from_str(text_proto)?;
        let mut binary_proto = Vec::new();
        storage_files.write_to_vec(&mut binary_proto)?;
        Ok(binary_proto)
    }

    pub fn write_proto_to_temp_file(text_proto: &str) -> Result<NamedTempFile, StorageProtoError> {
        let bytes = get_binary_proto_from_text_proto(text_proto).unwrap();
        let mut file = NamedTempFile::new()?;
        let _ = file.write_all(&bytes);
        Ok(file)
    }
}

#[cfg(test)]
mod tests {
    use storage_record_pb::StorageProtoError;

    use super::*;

    #[test]
    fn test_parse_storage_record_pb() {
        let text_proto = r#"
files {
    version: 0
    container: "system"
    package_map: "/system/etc/package.map"
    flag_map: "/system/etc/flag.map"
    flag_val: "/metadata/aconfig/system.val"
    timestamp: 12345
}
files {
    version: 1
    container: "product"
    package_map: "/product/etc/package.map"
    flag_map: "/product/etc/flag.map"
    flag_val: "/metadata/aconfig/product.val"
    timestamp: 54321
}
"#;
        let binary_proto_bytes =
            storage_record_pb::get_binary_proto_from_text_proto(text_proto).unwrap();
        let storage_files = storage_record_pb::try_from_binary_proto(&binary_proto_bytes).unwrap();
        assert_eq!(storage_files.files.len(), 2);
        let system_file = &storage_files.files[0];
        assert_eq!(system_file.version(), 0);
        assert_eq!(system_file.container(), "system");
        assert_eq!(system_file.package_map(), "/system/etc/package.map");
        assert_eq!(system_file.flag_map(), "/system/etc/flag.map");
        assert_eq!(system_file.flag_val(), "/metadata/aconfig/system.val");
        assert_eq!(system_file.timestamp(), 12345);
        let product_file = &storage_files.files[1];
        assert_eq!(product_file.version(), 1);
        assert_eq!(product_file.container(), "product");
        assert_eq!(product_file.package_map(), "/product/etc/package.map");
        assert_eq!(product_file.flag_map(), "/product/etc/flag.map");
        assert_eq!(product_file.flag_val(), "/metadata/aconfig/product.val");
        assert_eq!(product_file.timestamp(), 54321);
    }

    #[test]
    fn test_parse_invalid_storage_record_pb() {
        let text_proto = r#"
files {
    version: 0
    container: "system"
    package_map: ""
    flag_map: "/system/etc/flag.map"
    flag_val: "/metadata/aconfig/system.val"
    timestamp: 12345
}
"#;
        let binary_proto_bytes =
            storage_record_pb::get_binary_proto_from_text_proto(text_proto).unwrap();
        let err = storage_record_pb::try_from_binary_proto(&binary_proto_bytes).unwrap_err();
        assert!(
            matches!(err, StorageProtoError::MissingPackageMap { container } if container == "system")
        );

        let text_proto = r#"
files {
    version: 0
    container: "system"
    package_map: "/system/etc/package.map"
    flag_map: ""
    flag_val: "/metadata/aconfig/system.val"
    timestamp: 12345
}
"#;
        let binary_proto_bytes =
            storage_record_pb::get_binary_proto_from_text_proto(text_proto).unwrap();
        let err = storage_record_pb::try_from_binary_proto(&binary_proto_bytes).unwrap_err();
        assert!(
            matches!(err, StorageProtoError::MissingFlagMap { container } if container == "system")
        );

        let text_proto = r#"
files {
    version: 0
    container: "system"
    package_map: "/system/etc/package.map"
    flag_map: "/system/etc/flag.map"
    flag_val: ""
    timestamp: 12345
}
"#;
        let binary_proto_bytes =
            storage_record_pb::get_binary_proto_from_text_proto(text_proto).unwrap();
        let err = storage_record_pb::try_from_binary_proto(&binary_proto_bytes).unwrap_err();
        assert!(
            matches!(err, StorageProtoError::MissingFlagValue { container } if container == "system")
        );
    }
}
