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
$(warning SYSTEM_EXT_PUBLIC_POLICY=$(SYSTEM_EXT_PUBLIC_POLICY))
$(warning SYSTEM_EXT_PRIVATE_POLICY=$(SYSTEM_EXT_PRIVATE_POLICY))

PRODUCT_PUBLIC_POLICY := $(PRODUCT_PUBLIC_SEPOLICY_DIRS)
PRODUCT_PRIVATE_POLICY := $(PRODUCT_PRIVATE_SEPOLICY_DIRS)
$(warning PRODUCT_PUBLIC_POLICY=$(PRODUCT_PUBLIC_POLICY))
$(warning PRODUCT_PRIVATE_POLICY=$(PRODUCT_PRIVATE_POLICY))

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


