# Copyright (C) 2024 Google Inc.
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

# TODO: After Soong's recovery partition variation can be set to selectable
#       and the meta_lic file duplication issue is resolved, move it to the
#       dist section of the corresponding module's Android.bp.
my_dist_files := $(HOST_OUT_EXECUTABLES)/mke2fs
my_dist_files += $(HOST_OUT_EXECUTABLES)/make_f2fs
my_dist_files += $(HOST_OUT_EXECUTABLES)/make_f2fs_casefold
$(call dist-for-goals,dist_files sdk,$(my_dist_files))
my_dist_files :=
