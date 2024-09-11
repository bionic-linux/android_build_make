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

//! `aconfig_flags` is a crate for reading aconfig flags from Rust
// When building with the Android tool-chain
//
//   - an external crate `aconfig_flags` will be generated
//   - the feature "cargo" will be disabled
//
// When building with cargo
//
//   - the feature "cargo" will be enabled
//
// This module hides these differences from the rest of aconfig.

// ---- When building with the Android tool-chain ----
#[cfg(not(feature = "cargo"))]
pub mod auto_generated {
    pub fn enable_only_new_storage() -> bool {
        aconfig_flags_inner::enable_only_new_storage()
    }
}

// ---- When building with cargo ----
#[cfg(feature = "cargo")]
pub mod auto_generated {
    pub fn enable_only_new_storage() -> bool {
        true
    }
}