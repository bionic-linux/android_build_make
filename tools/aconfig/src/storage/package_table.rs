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

use crate::storage::{self, FlagPackage};
use anyhow::Result;

#[derive(PartialEq, Debug)]
pub struct PackageTableHeader<'a> {
    pub version: u32,
    pub container: &'a str,
    pub file_size: u32,
    pub num_packages: u32,
    pub bucket_offset: u32,
    pub node_offset: u32,
}

impl<'a> PackageTableHeader<'a> {
    fn new(container: &'a str, num_packages: u32) -> Self {
        PackageTableHeader {
            version: storage::FILE_VERSION,
            container,
            file_size: 0,
            num_packages,
            bucket_offset: 0,
            node_offset: 0,
        }
    }

    fn as_bytes(&self) -> Vec<u8> {
        let mut result = Vec::new();
        result.extend_from_slice(&self.version.to_le_bytes());
        let container_bytes = self.container.as_bytes();
        result.extend_from_slice(&(container_bytes.len() as u32).to_le_bytes());
        result.extend_from_slice(container_bytes);
        result.extend_from_slice(&self.file_size.to_le_bytes());
        result.extend_from_slice(&self.num_packages.to_le_bytes());
        result.extend_from_slice(&self.bucket_offset.to_le_bytes());
        result.extend_from_slice(&self.node_offset.to_le_bytes());
        result
    }
}

#[derive(PartialEq, Debug)]
pub struct PackageTableNode<'a> {
    pub package_name: &'a str,
    pub package_id: u32,
    pub boolean_offset: u32,
    pub next_offset: Option<u32>,
    pub bucket_index: u32,
}

impl<'a> PackageTableNode<'a> {
    fn new(package: &'a FlagPackage, num_buckets: u32) -> Self {
        let bucket_index =
            storage::get_bucket_index(&package.package_name.to_string(), num_buckets) as u32;
        PackageTableNode {
            package_name: package.package_name,
            package_id: package.package_id,
            boolean_offset: package.boolean_offset,
            next_offset: None,
            bucket_index,
        }
    }

    fn as_bytes(&self) -> Vec<u8> {
        let mut result = Vec::new();
        let name_bytes = self.package_name.as_bytes();
        result.extend_from_slice(&(name_bytes.len() as u32).to_le_bytes());
        result.extend_from_slice(name_bytes);
        result.extend_from_slice(&self.package_id.to_le_bytes());
        result.extend_from_slice(&self.boolean_offset.to_le_bytes());
        result.extend_from_slice(&self.next_offset.unwrap_or(0).to_le_bytes());
        result
    }
}

pub struct PackageTable<'a> {
    pub header: PackageTableHeader<'a>,
    pub buckets: Vec<Option<u32>>,
    pub nodes: Vec<PackageTableNode<'a>>,
}

impl<'a> PackageTable<'a> {
    pub fn new(container: &'a str, packages: &'a [FlagPackage<'a>]) -> Result<Self> {
        // create table
        let num_packages = packages.len() as u32;
        let num_buckets = storage::get_table_size(num_packages)?;
        let mut table = PackageTable {
            header: PackageTableHeader::new(container, num_packages),
            buckets: vec![None; num_buckets as usize],
            nodes: packages.iter().map(|pkg| PackageTableNode::new(pkg, num_buckets)).collect(),
        };

        // sort nodes by bucket index for efficiency
        table.nodes.sort_by(|a, b| a.bucket_index.cmp(&b.bucket_index));

        // fill all node offset
        let mut offset = 0;
        for i in 0..table.nodes.len() {
            let node_bucket_idx = table.nodes[i].bucket_index;
            let next_node_bucket_idx = if i + 1 < table.nodes.len() {
                Some(table.nodes[i + 1].bucket_index)
            } else {
                None
            };

            if table.buckets[node_bucket_idx as usize].is_none() {
                table.buckets[node_bucket_idx as usize] = Some(offset);
            }
            offset += table.nodes[i].as_bytes().len() as u32;

            if let Some(index) = next_node_bucket_idx {
                if index == node_bucket_idx {
                    table.nodes[i].next_offset = Some(offset);
                }
            }
        }

        // fill table region offset
        table.header.bucket_offset = table.header.as_bytes().len() as u32;
        table.header.node_offset = table.header.bucket_offset + num_buckets * 4;
        table.header.file_size = table.header.node_offset
            + table.nodes.iter().map(|x| x.as_bytes().len()).sum::<usize>() as u32;

        Ok(table)
    }

    pub fn as_bytes(&self) -> Vec<u8> {
        [
            self.header.as_bytes(),
            self.buckets.iter().map(|v| v.unwrap_or(0).to_le_bytes()).collect::<Vec<_>>().concat(),
            self.nodes.iter().map(|v| v.as_bytes()).collect::<Vec<_>>().concat(),
        ]
        .concat()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::storage::{group_flags_by_package, tests::parse_all_test_flags};

    #[test]
    fn test_table_contents() {
        let caches = parse_all_test_flags();
        let packages = group_flags_by_package(caches.iter());
        let package_table = PackageTable::new("system", &packages);
        assert!(package_table.is_ok());

        let header: &PackageTableHeader = &package_table.as_ref().unwrap().header;
        let expected_header = PackageTableHeader {
            version: storage::FILE_VERSION,
            container: "system",
            file_size: 158,
            num_packages: 2,
            bucket_offset: 30,
            node_offset: 58,
        };
        assert_eq!(header, &expected_header);

        let buckets: &Vec<Option<u32>> = &package_table.as_ref().unwrap().buckets;
        let expected: Vec<Option<u32>> = vec![Some(0), None, None, Some(50), None, None, None];
        assert_eq!(buckets, &expected);

        let nodes: &Vec<PackageTableNode> = &package_table.as_ref().unwrap().nodes;
        assert_eq!(nodes.len(), 2);
        let first_node_expected = PackageTableNode {
            package_name: "com.android.aconfig.storage.test_2",
            package_id: 1,
            boolean_offset: 10,
            next_offset: None,
            bucket_index: 0,
        };
        assert_eq!(nodes[0], first_node_expected);
        let second_node_expected = PackageTableNode {
            package_name: "com.android.aconfig.storage.test_1",
            package_id: 0,
            boolean_offset: 0,
            next_offset: None,
            bucket_index: 3,
        };
        assert_eq!(nodes[1], second_node_expected);
    }
}
