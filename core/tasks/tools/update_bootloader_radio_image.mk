# Copyright (C) 2024 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

ifeq ($(USES_DEVICE_GOOGLE_ZUMA),true)
    -include vendor/google_devices/zuma/prebuilts/misc_bins/update_bootloader_radio_image.mk
endif
ifeq ($(USES_DEVICE_GOOGLE_ZUMAPRO),true)
    -include vendor/google_devices/zumapro/prebuilts/misc_bins/update_bootloader_radio_image.mk
endif
ifeq ($(USES_DEVICE_GOOGLE_LAGUNA),true)
    -include vendor/google_devices/laguna/prebuilts/misc_bins/update_bootloader_radio_image.mk
endif
ifeq ($(USES_DEVICE_GOOGLE_MALIBU),true)
    -include vendor/google_devices/malibu/prebuilts/misc_bins/update_bootloader_radio_image.mk
endif
