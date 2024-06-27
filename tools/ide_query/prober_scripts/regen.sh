#!/bin/bash -ex

# Copyright (C) 2024 The Android Open Source Project
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

cd $(dirname $BASH_SOURCE)
source $(pwd)/../../../shell_utils.sh
require_top

files_to_build=(
  build/make/tools/ide_query/prober_scripts/general.cc
)

cd ${TOP}
build/make/tools/ide_query/ide_query.sh --lunch_target=aosp_arm-trunk_staging-eng ${files_to_build[@]} > build/make/tools/ide_query/prober_scripts/ide_query.out
