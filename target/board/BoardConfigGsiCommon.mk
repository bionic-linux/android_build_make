# BoardConfigGsiCommon.mk
#
# Common compile-time definitions for GSI
# Builds upon the mainline config.
#

include build/make/target/board/BoardConfigMainlineCommon.mk

# Enable system property split for Treble
BOARD_PROPERTY_OVERRIDES_SPLIT_ENABLED := true

# This flag is set by mainline but isn't desired for GSI.
BOARD_USES_SYSTEM_OTHER_ODEX :=

# GSIs are historically released in sparse format.
# Some vendors' bootloaders don't work properly with raw format images. So
# we explicit specify this need below (even though it's the current default).
TARGET_USERIMAGES_SPARSE_EXT_DISABLED := false

# system.img is always ext4 with sparse option
# GSI also includes make_f2fs to support userdata parition in f2fs
# for some devices
TARGET_USERIMAGES_USE_F2FS := true

# Enable dynamic system image size and reserved 64MB in it.
BOARD_SYSTEMIMAGE_PARTITION_RESERVED_SIZE := 67108864

# GSI forces product packages to /system for now.
TARGET_COPY_OUT_PRODUCT := system/product

# Creates metadata partition mount point under root for
# the devices with metadata parition
BOARD_USES_METADATA_PARTITION := true

# GSI specific System Properties
ifneq (,$(filter userdebug eng,$(TARGET_BUILD_VARIANT)))
TARGET_SYSTEM_PROP := build/make/target/board/gsi_system.prop
else
TARGET_SYSTEM_PROP := build/make/target/board/gsi_system_user.prop
endif

# Set this to create /cache mount point for non-A/B devices that mounts /cache.
# The partition size doesn't matter, just to make build pass.
BOARD_CACHEIMAGE_FILE_SYSTEM_TYPE := ext4
BOARD_CACHEIMAGE_PARTITION_SIZE := 16777216

# Disable 64 bit mediadrmserver
TARGET_ENABLE_MEDIADRM_64 :=

# Ordinary (non-flattened) APEX may require kernel changes. For maximum compatibility,
# use flattened APEX for GSI
TARGET_FLATTEN_APEX := true
