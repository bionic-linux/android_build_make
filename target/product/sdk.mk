#
# Copyright (C) 2007 The Android Open Source Project
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

PRODUCT_POLICY := android.policy_phone
PRODUCT_PROPERTY_OVERRIDES :=

PRODUCT_PACKAGES := \
	Calculator \
	Camera \
	DeskClock \
	Email \
	Exchange \
	Gallery \
	Music \
	Mms \
	OpenWnn \
	libWnnEngDic \
	libWnnJpnDic \
	libwnndict \
	Phone \
	PinyinIME \
	Protips \
	SoftKeyboard \
	SystemUI \
	Launcher2 \
	Development \
	DrmProvider \
	Fallback \
	Settings \
	SdkSetup \
	CustomLocale \
	sqlite3 \
	LatinIME \
	CertInstaller \
	LiveWallpapersPicker \
	ApiDemos \
	GestureBuilder \
	CubeLiveWallpapers \
	QuickSearchBox \
	WidgetPreview \
	monkeyrunner \
	guavalib \
	jsr305lib \
	jython \
	jsilver \
	librs_jni \
	CalendarProvider \
	Calendar

# Define the host tools and libs that are parts of the SDK.
include sdk/build/product_sdk.mk
include development/build/product_sdk.mk

# audio libraries.
PRODUCT_PACKAGES += \
	audio.primary.goldfish \
	audio_policy.default

PRODUCT_PACKAGE_OVERLAYS := development/sdk_overlay

PRODUCT_COPY_FILES := \
	system/core/rootdir/etc/vold.fstab:system/etc/vold.fstab \
	frameworks/base/data/sounds/effects/camera_click.ogg:system/media/audio/ui/camera_click.ogg \
	frameworks/base/data/sounds/effects/VideoRecord.ogg:system/media/audio/ui/VideoRecord.ogg \
	frameworks/base/data/etc/handheld_core_hardware.xml:system/etc/permissions/handheld_core_hardware.xml \
	frameworks/base/data/etc/android.hardware.touchscreen.multitouch.jazzhand.xml:system/etc/permissions/android.hardware.touchscreen.multitouch.jazzhand.xml \
	frameworks/base/data/etc/android.hardware.camera.autofocus.xml:system/etc/permissions/android.hardware.camera.autofocus.xml \
        frameworks/base/media/libeffects/data/audio_effects.conf:system/etc/audio_effects.conf

$(call inherit-product-if-exists, frameworks/base/data/fonts/fonts.mk)
$(call inherit-product-if-exists, frameworks/base/data/keyboards/keyboards.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/core.mk)

# Overrides
PRODUCT_BRAND := generic
PRODUCT_NAME := sdk
PRODUCT_DEVICE := generic

# locale + densities. en_US is both first and in alphabetical order to
# ensure this is the default locale.
PRODUCT_LOCALES = \
	en_US \
	ldpi \
	hdpi \
	mdpi \
	xhdpi \
	ar_EG \
	ar_IL \
	bg_BG \
	ca_ES \
	cs_CZ \
	da_DK \
	de_AT \
	de_CH \
	de_DE \
	de_LI \
	el_GR \
	en_AU \
	en_CA \
	en_GB \
	en_IE \
	en_IN \
	en_NZ \
	en_SG \
	en_US \
	en_ZA \
	es_ES \
	es_US \
	fi_FI \
	fr_BE \
	fr_CA \
	fr_CH \
	fr_FR \
	he_IL \
	hi_IN \
	hr_HR \
	hu_HU \
	id_ID \
	it_CH \
	it_IT \
	ja_JP \
	ko_KR \
	lt_LT \
	lv_LV \
	nb_NO \
	nl_BE \
	nl_NL \
	pl_PL \
	pt_BR \
	pt_PT \
	ro_RO \
	ru_RU \
	sk_SK \
	sl_SI \
	sr_RS \
	sv_SE \
	th_TH \
	tl_PH \
	tr_TR \
	uk_UA \
	vi_VN \
	zh_CN \
	zh_TW

# include available languages for TTS in the system image
-include external/svox/pico/lang/PicoLangDeDeInSystem.mk
-include external/svox/pico/lang/PicoLangEnGBInSystem.mk
-include external/svox/pico/lang/PicoLangEnUsInSystem.mk
-include external/svox/pico/lang/PicoLangEsEsInSystem.mk
-include external/svox/pico/lang/PicoLangFrFrInSystem.mk
-include external/svox/pico/lang/PicoLangItItInSystem.mk
