#
# Copyright (C) 2013 The Android Open Source Project
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

PRODUCT_PROPERTY_OVERRIDES := \
    ro.config.notification_sound=OnTheHunt.ogg \
    ro.config.alarm_alert=Alarm_Classic.ogg

PRODUCT_PACKAGES += \
    Home \
    TelephonyProvider \
    UserDictionaryProvider \
    libandroidfw \
    libaudioutils \
    libmdnssd \
    libnfc_ndef \
    libpowermanager \
    libspeexresampler \
    libvariablespeed \
    libwebrtc_audio_preprocessing \

$(call inherit-product, $(SRC_TARGET_DIR)/product/core_minimal.mk)
