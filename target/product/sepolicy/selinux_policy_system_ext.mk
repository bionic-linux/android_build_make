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

SEPOLICY_SYSTEM_EXT_MODULES :=
include build/make/target/product/sepolicy/dir_flags.mk

ifneq ($(PRODUCT_PRECOMPILED_SEPOLICY),false)
ifdef HAS_SYSTEM_EXT_SEPOLICY
SEPOLICY_SYSTEM_EXT_MODULES += system_ext_sepolicy_and_mapping.sha256
endif
endif

ifdef HAS_SYSTEM_EXT_SEPOLICY
SEPOLICY_SYSTEM_EXT_MODULES += system_ext_sepolicy.cil
endif

ifdef HAS_SYSTEM_EXT_PUBLIC_SEPOLICY
SEPOLICY_SYSTEM_EXT_MODULES += \
    system_ext_mapping_file

system_ext_compat_files := $(call build_policy, $(sepolicy_compat_files), $(SYSTEM_EXT_PRIVATE_POLICY))

SEPOLICY_SYSTEM_EXT_MODULES += $(addprefix system_ext_, $(notdir $(system_ext_compat_files)))

endif

ifdef HAS_SYSTEM_EXT_SEPOLICY_DIR
SEPOLICY_SYSTEM_EXT_MODULES += \
    system_ext_file_contexts \
    system_ext_file_contexts_test \
    system_ext_keystore2_key_contexts \
    system_ext_hwservice_contexts \
    system_ext_hwservice_contexts_test \
    system_ext_property_contexts \
    system_ext_property_contexts_test \
    system_ext_seapp_contexts \
    system_ext_service_contexts \
    system_ext_service_contexts_test \
    system_ext_mac_permissions.xml \
    system_ext_bug_map \
    $(addprefix system_ext_,$(addsuffix .compat.cil,$(PLATFORM_SEPOLICY_COMPAT_VERSIONS))) \

endif

