#
# Copyright (C) 2019 The Android Open-Source Project
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

# Device makers who are willing to support booting the public Developer-GSI
# in locked state can add the following line into a device.mk to inherit this
# makefile. This file will then install the up-to-date GSI public keys into
# the first-stage ramdisk to pass verified boot.
#
# In device/<company>/<board>/device.mk:
#   $(call inherit-product, $(SRC_TARGET_DIR)/product/developer_gsi_keys.mk)
#
# Currently, the developer GSI images can be downloaded from the following URL:
#   https://developer.android.com/topic/generic-system-image/releases
#
ifeq ($(BOARD_MOVE_GSI_AVB_KEYS_TO_VENDOR_BOOT),true) # AVB keys are installed to vendor ramdisk
  ifeq ($(BOARD_MOVE_RECOVERY_RESOURCES_TO_VENDOR_BOOT),true) # no dedicated recovery partition
    my_gsi_avb_keys_path := $(TARGET_VENDOR_RAMDISK_OUT)/first_stage_ramdisk/avb
  else # device has a dedicated recovery partition
    my_gsi_avb_keys_path := $(TARGET_VENDOR_RAMDISK_OUT)/avb
  endif
else
  ifeq ($(BOARD_USES_RECOVERY_AS_BOOT),true) # no dedicated recovery partition
    my_gsi_avb_keys_path := $(TARGET_RECOVERY_ROOT_OUT)/first_stage_ramdisk/avb
  else # device has a dedicated recovery partition
    my_gsi_avb_keys_path := $(TARGET_RAMDISK_OUT)/avb
  endif
endif

# q-developer-gsi.avbpubkey
PRODUCT_COPY_FILES += system/core/rootdir/avb/q-developer-gsi.avbpubkey:$(my_gsi_avb_keys_path)/q-developer-gsi.avbpubkey

# r-developer-gsi.avbpubkey
PRODUCT_COPY_FILES += system/core/rootdir/avb/r-developer-gsi.avbpubkey:$(my_gsi_avb_keys_path)/r-developer-gsi.avbpubkey

# s-developer-gsi.avbpubkey
PRODUCT_COPY_FILES += system/core/rootdir/avb/s-developer-gsi.avbpubkey:$(my_gsi_avb_keys_path)/s-developer-gsi.avbpubkey
