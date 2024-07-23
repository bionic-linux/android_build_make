with_asan := false
ifneq (,$(filter address,$(SANITIZE_TARGET)))
  with_asan := true
endif

# SEPolicy versions

# PLATFORM_SEPOLICY_VERSION is a number of the form "YYYYMM" with "YYYYMM"
# mapping to vFRC version.
PLATFORM_SEPOLICY_VERSION := $(RELEASE_BOARD_API_LEVEL)
BOARD_SEPOLICY_VERS := $(PLATFORM_SEPOLICY_VERSION)
.KATI_READONLY := PLATFORM_SEPOLICY_VERSION BOARD_SEPOLICY_VERS

# A list of SEPolicy versions, besides PLATFORM_SEPOLICY_VERSION, that the framework supports.
PLATFORM_SEPOLICY_COMPAT_VERSIONS := $(filter-out $(PLATFORM_SEPOLICY_VERSION), \
    29.0 \
    30.0 \
    31.0 \
    32.0 \
    33.0 \
    34.0 \
    202404 \
    )

.KATI_READONLY := \
    PLATFORM_SEPOLICY_COMPAT_VERSIONS \
    PLATFORM_SEPOLICY_VERSION \

SEPOLICY_SYSTEM_MODULES := \
    plat_mapping_file \
    $(addprefix plat_,$(addsuffix .cil,$(PLATFORM_SEPOLICY_COMPAT_VERSIONS))) \
    $(addsuffix .compat.cil,$(PLATFORM_SEPOLICY_COMPAT_VERSIONS)) \
    plat_sepolicy.cil \
    secilc \

ifneq ($(PRODUCT_PRECOMPILED_SEPOLICY),false)
SEPOLICY_SYSTEM_MODULES += plat_sepolicy_and_mapping.sha256
endif

SEPOLICY_SYSTEM_MODULES_HOST := \
    build_sepolicy \
    searchpolicy \

SEPOLICY_SYSTEM_MODULES += \
    plat_file_contexts \
    plat_file_contexts_test \
    plat_keystore2_key_contexts \
    plat_mac_permissions.xml \
    plat_property_contexts \
    plat_property_contexts_test \
    plat_seapp_contexts \
    plat_service_contexts \
    plat_service_contexts_test \
    plat_hwservice_contexts \
    plat_hwservice_contexts_test \
    fuzzer_bindings_test \
    plat_bug_map \

ifneq ($(with_asan),true)
ifneq ($(SELINUX_IGNORE_NEVERALLOWS),true)
SEPOLICY_SYSTEM_MODULES += \
    sepolicy_compat_test \
    sepolicy_test \
    sepolicy_dev_type_test \

SEPOLICY_SYSTEM_MODULES += \
    $(addprefix treble_sepolicy_tests_,$(PLATFORM_SEPOLICY_COMPAT_VERSIONS)) \

endif  # SELINUX_IGNORE_NEVERALLOWS
endif  # with_asan

ifeq ($(RELEASE_BOARD_API_LEVEL_FROZEN),true)
SEPOLICY_SYSTEM_MODULES += \
    se_freeze_test
endif

