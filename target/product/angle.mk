#
# Copyright 2023 The Android Open-Source Project
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

# To include ANGLE drivers into the build, add
# $(call inherit-product, $(SRC_TARGET_DIR)/product/angle.mk) to the Makefile.

PRODUCT_PACKAGES += \
    libEGL_angle \
    libGLESv1_CM_angle \
    libGLESv2_angle

# Set ro.gfx.angle.supported based on if ANGLE is installed in vendor partition
PRODUCT_VENDOR_PROPERTIES += ro.gfx.angle.supported=true

# Indicate whether ANGLE is the default system GLES driver, by default this is
# false because ANGLE can coexist with native system GLES driver.
USE_ANGLE ?= false

ifeq ($(USE_ANGLE),true)

PRODUCT_VENDOR_PROPERTIES += \
    persist.graphics.egl=angle

endif
