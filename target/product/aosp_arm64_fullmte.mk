# Copyright (C) 2023 The Android Open-Source Project
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

include $(SRC_TARGET_DIR)/product/fullmte.mk

# Enable mainline checking for excat this product name
ifeq (aosp_arm64_fullmte,$(TARGET_PRODUCT))
  PRODUCT_ENFORCE_ARTIFACT_PATH_REQUIREMENTS := relaxed
endif

$(call inherit-product, $(SRC_TARGET_DIR)/product/aosp_arm64.mk)

ifeq (aosp_arm64_fullmte,$(TARGET_PRODUCT))
  # Build modules from source if this has not been pre-configured
  MODULE_BUILD_FROM_SOURCE ?= true

  $(call inherit-product, $(SRC_TARGET_DIR)/product/gsi_release.mk)
endif

PRODUCT_NAME := aosp_arm64_fullmte
