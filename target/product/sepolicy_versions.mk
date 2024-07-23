#
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
#

# SEPolicy versions

# PLATFORM_SEPOLICY_VERSION is a number of the form "YYYYMM" with "YYYYMM"
# mapping to vFRC version.
PLATFORM_SEPOLICY_VERSION ?= $(RELEASE_BOARD_API_LEVEL)
BOARD_SEPOLICY_VERS ?= $(PLATFORM_SEPOLICY_VERSION)
.KATI_READONLY := PLATFORM_SEPOLICY_VERSION BOARD_SEPOLICY_VERS

# A list of SEPolicy versions, besides PLATFORM_SEPOLICY_VERSION, that the framework supports.
PLATFORM_SEPOLICY_COMPAT_VERSIONS ?= $(filter-out $(PLATFORM_SEPOLICY_VERSION), \
    29.0 \
    30.0 \
    31.0 \
    32.0 \
    33.0 \
    34.0 \
    202404 \
    )
.KATI_READONLY := \
    PLATFORM_SEPOLICY_COMPAT_VERSIONS \
