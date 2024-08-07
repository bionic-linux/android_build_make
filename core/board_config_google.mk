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

# ###############################################################
# This file adds google hardware variables into soong config namespace (`google`)
# ###############################################################

ifeq ($(BOARD_USES_VENDORIMAGE), true)
$(call soong_config_set,google,board_uses_vendorimage,true)
endif

ifeq ($(HWC_NO_SUPPORT_SKIP_VALIDATE),true)
$(call soong_config_set,google,hwc_no_support_skip_validate,true)
endif

ifeq ($(HWC_SUPPORT_COLOR_TRANSFORM), true)
$(call soong_config_set,google,hwc_support_color_transform,true)
endif

ifeq ($(HWC_SUPPORT_RENDER_INTENT), true)
$(call soong_config_set,google,hwc_support_render_intent,true)
endif

ifeq ($(BOARD_USES_VIRTUAL_DISPLAY), true)
$(call soong_config_set,google,board_uses_virtual_display,true)
endif

ifeq ($(BOARD_USES_DT), true)
$(call soong_config_set,google,board_uses_dt,true)
endif

ifeq ($(USES_IDISPLAY_INTF_SEC),true)
$(call soong_config_set,google,uses_idisplay_intf_sec,true)
endif
