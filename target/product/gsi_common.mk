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

$(call inherit-product, $(SRC_TARGET_DIR)/product/mainline_system.mk)

# GSI includes all AOSP product packages and placed under /system/product
$(call inherit-product, $(SRC_TARGET_DIR)/product/handheld_product.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/telephony_product.mk)

# Default AOSP sounds
$(call inherit-product-if-exists, frameworks/base/data/sounds/AllAudio.mk)

# Additional settings used in all AOSP builds
PRODUCT_PROPERTY_OVERRIDES := \
    ro.config.ringtone=Ring_Synth_04.ogg \
    ro.config.notification_sound=pixiedust.ogg

# The mainline checking whitelist, should be clean up
PRODUCT_ARTIFACT_PATH_REQUIREMENT_WHITELIST := \
    system/app/messaging/messaging.apk \
    system/app/PhotoTable/PhotoTable.apk \
    system/app/WAPPushManager/WAPPushManager.apk \
    system/etc/seccomp_policy/crash_dump.%.policy \
    system/etc/seccomp_policy/mediacodec.policy \
    system/lib/libframesequence.so \
    system/lib/libgiftranscode.so \
    system/lib64/libframesequence.so \
    system/lib64/libgiftranscode.so \

# Modules that are to be moved to /product
PRODUCT_ARTIFACT_PATH_REQUIREMENT_WHITELIST += \
  system/app/Browser2/Browser2.apk \
  system/app/Calendar/Calendar.apk \
  system/app/Camera2/Camera2.apk \
  system/app/DeskClock/DeskClock.apk \
  system/app/DeskClock/oat/arm64/DeskClock.odex \
  system/app/DeskClock/oat/arm64/DeskClock.vdex \
  system/app/Email/Email.apk \
  system/app/Gallery2/Gallery2.apk \
  system/app/LatinIME/LatinIME.apk \
  system/app/LatinIME/oat/arm64/LatinIME.odex \
  system/app/LatinIME/oat/arm64/LatinIME.vdex \
  system/app/Music/Music.apk \
  system/app/QuickSearchBox/QuickSearchBox.apk \
  system/app/webview/webview.apk \
  system/bin/healthd \
  system/etc/init/healthd.rc \
  system/etc/vintf/manifest/manifest_healthd.xml \
  system/lib64/libjni_eglfence.so \
  system/lib64/libjni_filtershow_filters.so \
  system/lib64/libjni_jpegstream.so \
  system/lib64/libjni_jpegutil.so \
  system/lib64/libjni_latinime.so \
  system/lib64/libjni_tinyplanet.so \
  system/priv-app/CarrierConfig/CarrierConfig.apk \
  system/priv-app/CarrierConfig/oat/arm64/CarrierConfig.odex \
  system/priv-app/CarrierConfig/oat/arm64/CarrierConfig.vdex \
  system/priv-app/Contacts/Contacts.apk \
  system/priv-app/Dialer/Dialer.apk \
  system/priv-app/Launcher3QuickStep/Launcher3QuickStep.apk \
  system/priv-app/OneTimeInitializer/OneTimeInitializer.apk \
  system/priv-app/Provision/Provision.apk \
  system/priv-app/SettingsIntelligence/SettingsIntelligence.apk \
  system/priv-app/StorageManager/StorageManager.apk \
  system/priv-app/WallpaperCropper/WallpaperCropper.apk \

# Some GSI builds enable dexpreopt, whitelist these preopt files
PRODUCT_ARTIFACT_PATH_REQUIREMENT_WHITELIST += %.odex %.vdex %.art

# Exclude GSI specific files
PRODUCT_ARTIFACT_PATH_REQUIREMENT_WHITELIST += \
    system/etc/init/config/skip_mount.cfg \
    system/etc/init/init.gsi.rc \

# Exclude all files under system/product and system/product_services
PRODUCT_ARTIFACT_PATH_REQUIREMENT_WHITELIST += \
    system/product/% \
    system/product_services/%


# Split selinux policy
PRODUCT_FULL_TREBLE_OVERRIDE := true

# Enable dynamic partition size
PRODUCT_USE_DYNAMIC_PARTITION_SIZE := true

# Enable A/B update
AB_OTA_UPDATER := true
AB_OTA_PARTITIONS := system

# Needed by Pi newly launched device to pass VtsTrebleSysProp on GSI
PRODUCT_COMPATIBLE_PROPERTY_OVERRIDE := true

# GSI specific tasks on boot
PRODUCT_COPY_FILES += \
    build/make/target/product/gsi/skip_mount.cfg:system/etc/init/config/skip_mount.cfg \
    build/make/target/product/gsi/init.gsi.rc:system/etc/init/init.gsi.rc \

# Support addtional P vendor interface
PRODUCT_EXTRA_VNDK_VERSIONS := 28

# Default AOSP packages
PRODUCT_PACKAGES += \
    messaging \

# Default AOSP packages
PRODUCT_PACKAGES += \
    PhotoTable \
    WAPPushManager \

# Telephony:
#   Provide a APN configuration to GSI product
PRODUCT_COPY_FILES += \
    device/sample/etc/apns-full-conf.xml:$(TARGET_COPY_OUT_PRODUCT)/etc/apns-conf.xml

# NFC:
#   Provide a libnfc-nci.conf to GSI product
PRODUCT_COPY_FILES += \
    device/generic/common/nfc/libnfc-nci.conf:$(TARGET_COPY_OUT_PRODUCT)/etc/libnfc-nci.conf
