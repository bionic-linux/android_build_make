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

use crate::package_table::{PackageTable, PackageTableNode, PackageTableHeader};
use crate::StorageFileType;

pub fn create_test_v1_package_table_bytes() -> Vec<u8> {
    let package_table = create_test_v1_package_table();

    let mut result = Vec::new();
    result.extend_from_slice(&1u32.to_le_bytes());
    let container_bytes = package_table.header.container.as_bytes();
    result.extend_from_slice(&(container_bytes.len() as u32).to_le_bytes());
    result.extend_from_slice(container_bytes);
    result.extend_from_slice(&package_table.header.file_type.to_le_bytes());
    result.extend_from_slice(&package_table.header.file_size.to_le_bytes());
    result.extend_from_slice(&package_table.header.num_packages.to_le_bytes());
    result.extend_from_slice(&package_table.header.bucket_offset.to_le_bytes());
    result.extend_from_slice(&package_table.header.node_offset.to_le_bytes());

    result.extend_from_slice(
        &package_table
            .buckets
            .iter()
            .map(|v| v.unwrap_or(0).to_le_bytes())
            .collect::<Vec<_>>()
            .concat(),
    );

    for node in &package_table.nodes {
        let mut node_bytes = Vec::new();
        let name_bytes = node.package_name.as_bytes();
        node_bytes.extend_from_slice(&(name_bytes.len() as u32).to_le_bytes());
        node_bytes.extend_from_slice(name_bytes);
        node_bytes.extend_from_slice(&node.package_id.to_le_bytes());
        // Omit fingerprint, which was not present in v1.
        node_bytes.extend_from_slice(&node.boolean_start_index.to_le_bytes());
        node_bytes.extend_from_slice(&node.next_offset.unwrap_or(0).to_le_bytes());

        result.extend_from_slice(&node_bytes);
    }
    result
}

fn create_test_v1_package_table() -> PackageTable {
    let header = PackageTableHeader {
        version: 1,
        container: String::from("mockup"),
        file_type: StorageFileType::PackageMap as u8,
        file_size: 209,
        num_packages: 3,
        bucket_offset: 31,
        node_offset: 59,
    };
    let buckets: Vec<Option<u32>> = vec![Some(59), None, None, Some(109), None, None, None];
    let first_node = PackageTableNode {
        package_name: String::from("com.android.aconfig.storage.test_2"),
        package_id: 1,
        fingerprint: 0,
        boolean_start_index: 3,
        next_offset: None,
    };
    let second_node = PackageTableNode {
        package_name: String::from("com.android.aconfig.storage.test_1"),
        package_id: 0,
        fingerprint: 0,
        boolean_start_index: 0,
        next_offset: Some(159),
    };
    let third_node = PackageTableNode {
        package_name: String::from("com.android.aconfig.storage.test_4"),
        package_id: 2,
        fingerprint: 0,
        boolean_start_index: 6,
        next_offset: None,
    };
    let nodes = vec![first_node, second_node, third_node];
    PackageTable { header, buckets, nodes }
}
