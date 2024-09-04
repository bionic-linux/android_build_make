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

SYSTEM_EXT_PUBLIC_POLICY := $(SYSTEM_EXT_PUBLIC_SEPOLICY_DIRS)
SYSTEM_EXT_PRIVATE_POLICY := $(SYSTEM_EXT_PRIVATE_SEPOLICY_DIRS)

PRODUCT_PUBLIC_POLICY := $(PRODUCT_PUBLIC_SEPOLICY_DIRS)
PRODUCT_PRIVATE_POLICY := $(PRODUCT_PRIVATE_SEPOLICY_DIRS)

ifneq (,$(SYSTEM_EXT_PUBLIC_POLICY)$(SYSTEM_EXT_PRIVATE_POLICY))
HAS_SYSTEM_EXT_SEPOLICY_DIR := true
endif

# TODO(b/119305624): Currently if the device doesn't have a product partition,
# we install product sepolicy into /system/product. We do that because bits of
# product sepolicy that's still in /system might depend on bits that have moved
# to /product. Once we finish migrating product sepolicy out of system, change
# it so that if no product partition is present, product sepolicy artifacts are
# not built and installed at all.
ifneq (,$(PRODUCT_PUBLIC_POLICY)$(PRODUCT_PRIVATE_POLICY))
HAS_PRODUCT_SEPOLICY_DIR := true
endif

ifeq ($(SELINUX_IGNORE_NEVERALLOWS),true)
ifeq ($(TARGET_BUILD_VARIANT),user)
$(error SELINUX_IGNORE_NEVERALLOWS := true cannot be used in user builds)
endif
$(warning Be careful when using the SELINUX_IGNORE_NEVERALLOWS flag. \
          It does not work in user builds and using it will \
          not stop you from failing CTS.)
endif

# BOARD_SEPOLICY_DIRS was used for vendor/odm sepolicy customization before.
# It has been replaced by BOARD_VENDOR_SEPOLICY_DIRS (mandatory) and
# BOARD_ODM_SEPOLICY_DIRS (optional). BOARD_SEPOLICY_DIRS is still allowed for
# backward compatibility, which will be merged into BOARD_VENDOR_SEPOLICY_DIRS.
ifdef BOARD_SEPOLICY_DIRS
BOARD_VENDOR_SEPOLICY_DIRS += $(BOARD_SEPOLICY_DIRS)
endif

###########################################################
# Compute policy files to be used in policy build.
# $(1): files to include
# $(2): directories in which to find files
###########################################################

define build_policy
$(strip $(foreach type, $(1), $(foreach file, $(addsuffix /$(type), $(2)), $(sort $(wildcard $(file))))))
endef

sepolicy_build_files := security_classes \
                        initial_sids \
                        access_vectors \
                        global_macros \
                        neverallow_macros \
                        mls_macros \
                        mls_decl \
                        mls \
                        policy_capabilities \
                        te_macros \
                        attributes \
                        ioctl_defines \
                        ioctl_macros \
                        *.te \
                        roles_decl \
                        roles \
                        users \
                        initial_sid_contexts \
                        fs_use \
                        genfs_contexts \
                        port_contexts

sepolicy_compat_files := $(foreach ver, $(PLATFORM_SEPOLICY_COMPAT_VERSIONS), \
                           $(addprefix compat/$(ver)/, $(addsuffix .cil, $(ver))))

# Security classes and permissions defined outside of system/sepolicy.
security_class_extension_files := $(call build_policy, security_classes access_vectors, \
  $(SYSTEM_EXT_PUBLIC_POLICY) $(SYSTEM_EXT_PRIVATE_POLICY) \
  $(PRODUCT_PUBLIC_POLICY) $(PRODUCT_PRIVATE_POLICY) \
  $(BOARD_VENDOR_SEPOLICY_DIRS) $(BOARD_ODM_SEPOLICY_DIRS))

ifneq (,$(strip $(security_class_extension_files)))
  $(error Only platform SELinux policy may define classes and permissions: $(strip $(security_class_extension_files)))
endif

ifdef HAS_SYSTEM_EXT_SEPOLICY_DIR
  # Checks if there are public system_ext policy files.
  policy_files := $(call build_policy, $(sepolicy_build_files), $(SYSTEM_EXT_PUBLIC_POLICY))
  ifneq (,$(strip $(policy_files)))
    HAS_SYSTEM_EXT_PUBLIC_SEPOLICY := true
  endif
  # Checks if there are public/private system_ext policy files.
  policy_files := $(call build_policy, $(sepolicy_build_files), $(SYSTEM_EXT_PUBLIC_POLICY) $(SYSTEM_EXT_PRIVATE_POLICY))
  ifneq (,$(strip $(policy_files)))
    HAS_SYSTEM_EXT_SEPOLICY := true
  endif
endif # ifdef HAS_SYSTEM_EXT_SEPOLICY_DIR

ifdef HAS_PRODUCT_SEPOLICY_DIR
  # Checks if there are public product policy files.
  policy_files := $(call build_policy, $(sepolicy_build_files), $(PRODUCT_PUBLIC_POLICY))
  ifneq (,$(strip $(policy_files)))
    HAS_PRODUCT_PUBLIC_SEPOLICY := true
  endif
  # Checks if there are public/private product policy files.
  policy_files := $(call build_policy, $(sepolicy_build_files), $(PRODUCT_PUBLIC_POLICY) $(PRODUCT_PRIVATE_POLICY))
  ifneq (,$(strip $(policy_files)))
    HAS_PRODUCT_SEPOLICY := true
  endif
endif # ifdef HAS_PRODUCT_SEPOLICY_DIR

