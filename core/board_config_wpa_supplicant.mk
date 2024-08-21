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
# This file adds wpa_supplicant_8 variables into soong config namespace (`wpa_supplicant_8`)
# ###############################################################

ifdef BOARD_HOSTAPD_DRIVER
ifneq ($(BOARD_HOSTAPD_DRIVER),NL80211)
    $(error BOARD_HOSTAPD_DRIVER set to $(BOARD_HOSTAPD_DRIVER) but current soong expected it should be NL80211 only!)
endif
endif

ifdef BOARD_WPA_SUPPLICANT_DRIVER
ifneq ($(BOARD_WPA_SUPPLICANT_DRIVER),NL80211)
    $(error BOARD_WPA_SUPPLICANT_DRIVER set to $(BOARD_WPA_SUPPLICANT_DRIVER) but current soong expected it should be NL80211 only!)
endif
endif 

# This is for CONFIG_DRIVER_NL80211_BRCM, CONFIG_DRIVER_NL80211_SYNA, CONFIG_DRIVER_NL80211_QCA
# And it is only used for a clags setting in driver.
$(call soong_config_set,wpa_supplicant_8,board_wlan_device,$(BOARD_WLAN_DEVICE))

# Belong to CONFIG_IEEE80211AX definition
ifeq ($(WIFI_FEATURE_HOSTAPD_11AX),true)
$(call soong_config_set,wpa_supplicant_8,hostapd_11ax,true)
endif

# PLATFORM_VERSION
$(call soong_config_set,wpa_supplicant_8,platform_version,$(PLATFORM_VERSION))

# BOARD_HOSTAPD_PRIVATE_LIB
$(call soong_config_set,wpa_supplicant_8,board_hostapd_private_lib,$(BOARD_HOSTAPD_PRIVATE_LIB))

ifeq ($(BOARD_HOSTAPD_PRIVATE_LIB),)
$(call soong_config_set,wpa_supplicant_8,hostapd_use_stub_lib,true)
endif

ifeq ($(BOARD_HOSTAPD_CONFIG_80211W_MFP_OPTIONAL),true)
$(call soong_config_set,wpa_supplicant_8,board_hostapd_config_80211w_mfp_optional,true)
endif

ifneq ($(BOARD_HOSTAPD_PRIVATE_LIB_EVENT),)
$(call soong_config_set,wpa_supplicant_8,board_hostapd_private_lib_event,true)
endif

