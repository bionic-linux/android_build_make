# Java prebuilt coming from Soong.
# Extra inputs:
# LOCAL_SOONG_BUILT_INSTALLED
# LOCAL_SOONG_CLASSES_JAR
# LOCAL_SOONG_HEADER_JAR
# LOCAL_SOONG_DEX_JAR
# LOCAL_SOONG_JACOCO_REPORT_CLASSES_JAR
# LOCAL_SOONG_DEXPREOPT_CONFIG

ifneq ($(LOCAL_MODULE_MAKEFILE),$(SOONG_ANDROID_MK))
  $(call pretty-error,soong_java_prebuilt.mk may only be used from Soong)
endif

LOCAL_MODULE_SUFFIX := .jar
LOCAL_BUILT_MODULE_STEM := javalib.jar

intermediates.COMMON := $(call local-intermediates-dir,COMMON)

full_classes_jar := $(intermediates.COMMON)/classes.jar
full_classes_pre_proguard_jar := $(intermediates.COMMON)/classes-pre-proguard.jar
full_classes_header_jar := $(intermediates.COMMON)/classes-header.jar
common_javalib.jar := $(intermediates.COMMON)/javalib.jar

ifdef LOCAL_SOONG_AAR
  LOCAL_ADDITIONAL_CHECKED_MODULE += $(LOCAL_SOONG_AAR)
endif

# Use the Soong output as the checkbuild target instead of LOCAL_BUILT_MODULE
# to avoid checkbuilds making an extra copy of every module.
LOCAL_CHECKED_MODULE := $(LOCAL_PREBUILT_MODULE_FILE)
LOCAL_ADDITIONAL_CHECKED_MODULE += $(LOCAL_SOONG_HEADER_JAR)
LOCAL_ADDITIONAL_CHECKED_MODULE += $(LOCAL_FULL_MANIFEST_FILE)
LOCAL_ADDITIONAL_CHECKED_MODULE += $(LOCAL_SOONG_DEXPREOPT_CONFIG)
LOCAL_ADDITIONAL_CHECKED_MODULE += $(LOCAL_SOONG_RESOURCE_EXPORT_PACKAGE)
LOCAL_ADDITIONAL_CHECKED_MODULE += $(LOCAL_SOONG_DEX_JAR)

#######################################
include $(BUILD_SYSTEM)/base_rules.mk
#######################################

ifdef LOCAL_SOONG_CLASSES_JAR
  $(eval $(call copy-one-file,$(LOCAL_SOONG_CLASSES_JAR),$(full_classes_jar)))
  $(eval $(call copy-one-file,$(LOCAL_SOONG_CLASSES_JAR),$(full_classes_pre_proguard_jar)))
  $(eval $(call add-dependency,$(LOCAL_BUILT_MODULE),$(full_classes_jar)))

  ifneq ($(TURBINE_ENABLED),false)
    ifdef LOCAL_SOONG_HEADER_JAR
      $(eval $(call copy-one-file,$(LOCAL_SOONG_HEADER_JAR),$(full_classes_header_jar)))
    else
      $(eval $(call copy-one-file,$(full_classes_jar),$(full_classes_header_jar)))
    endif
  endif # TURBINE_ENABLED != false
endif

$(eval $(call copy-one-file,$(LOCAL_PREBUILT_MODULE_FILE),$(LOCAL_BUILT_MODULE)))

ifdef LOCAL_SOONG_JACOCO_REPORT_CLASSES_JAR
  $(eval $(call copy-one-file,$(LOCAL_SOONG_JACOCO_REPORT_CLASSES_JAR),\
    $(call local-packaging-dir,jacoco)/jacoco-report-classes.jar))
  $(call add-dependency,$(common_javalib.jar),\
    $(call local-packaging-dir,jacoco)/jacoco-report-classes.jar)
endif

ifdef LOCAL_SOONG_PROGUARD_DICT
  $(eval $(call copy-one-file,$(LOCAL_SOONG_PROGUARD_DICT),\
    $(intermediates.COMMON)/proguard_dictionary))
  $(eval $(call copy-one-file,$(LOCAL_SOONG_PROGUARD_DICT),\
    $(call local-packaging-dir,proguard_dictionary)/proguard_dictionary))
  $(eval $(call copy-one-file,$(LOCAL_SOONG_CLASSES_JAR),\
    $(call local-packaging-dir,proguard_dictionary)/classes.jar))
  $(call add-dependency,$(common_javalib.jar),\
    $(intermediates.COMMON)/proguard_dictionary)
  $(call add-dependency,$(common_javalib.jar),\
    $(call local-packaging-dir,proguard_dictionary)/proguard_dictionary)
  $(call add-dependency,$(common_javalib.jar),\
    $(call local-packaging-dir,proguard_dictionary)/classes.jar)
endif

ifdef LOCAL_SOONG_PROGUARD_USAGE_ZIP
  $(eval $(call copy-one-file,$(LOCAL_SOONG_PROGUARD_USAGE_ZIP),\
    $(call local-packaging-dir,proguard_usage)/proguard_usage.zip))
  $(call add-dependency,$(common_javalib.jar),\
    $(call local-packaging-dir,proguard_usage)/proguard_usage.zip)
endif


ifdef LOCAL_SOONG_RESOURCE_EXPORT_PACKAGE
  my_res_package := $(intermediates.COMMON)/package-res.apk

  $(my_res_package): $(LOCAL_SOONG_RESOURCE_EXPORT_PACKAGE)
	@echo "Copy: $@"
	$(copy-file-to-target)

  $(call add-dependency,$(LOCAL_BUILT_MODULE),$(my_res_package))

  my_proguard_flags := $(intermediates.COMMON)/export_proguard_flags
  $(my_proguard_flags): $(LOCAL_SOONG_EXPORT_PROGUARD_FLAGS)
	@echo "Export proguard flags: $@"
	rm -f $@
	touch $@
	for f in $+; do \
		echo -e "\n# including $$f" >>$@; \
		cat $$f >>$@; \
	done

  $(call add-dependency,$(LOCAL_BUILT_MODULE),$(my_proguard_flags))

  my_static_library_extra_packages := $(intermediates.COMMON)/extra_packages
  $(eval $(call copy-one-file,$(LOCAL_SOONG_STATIC_LIBRARY_EXTRA_PACKAGES),$(my_static_library_extra_packages)))
  $(call add-dependency,$(LOCAL_BUILT_MODULE),$(my_static_library_extra_packages))

  my_static_library_android_manifest := $(intermediates.COMMON)/manifest/AndroidManifest.xml
  $(eval $(call copy-one-file,$(LOCAL_FULL_MANIFEST_FILE),$(my_static_library_android_manifest)))
  $(call add-dependency,$(LOCAL_BUILT_MODULE),$(my_static_library_android_manifest))
endif # LOCAL_SOONG_RESOURCE_EXPORT_PACKAGE


ifdef LOCAL_SOONG_DEX_JAR
  ifndef LOCAL_IS_HOST_MODULE
    boot_jars := $(foreach pair,$(PRODUCT_BOOT_JARS), $(call word-colon,2,$(pair)))
    ifneq ($(filter $(LOCAL_MODULE),$(boot_jars)),) # is_boot_jar
      ifeq (true,$(WITH_DEXPREOPT))
        # $(DEFAULT_DEX_PREOPT_INSTALLED_IMAGE_MODULE) contains modules that installs
        # all of bootjars' dexpreopt files (.art, .oat, .vdex, ...)
        # Add them to the required list so they are installed alongside this module.
        ALL_MODULES.$(my_register_name).REQUIRED_FROM_TARGET += \
          $(DEFAULT_DEX_PREOPT_INSTALLED_IMAGE_MODULE) \
          $(2ND_DEFAULT_DEX_PREOPT_INSTALLED_IMAGE_MODULE)
        # Copy $(LOCAL_BUILT_MODULE) and its dependencies when installing boot.art
        # so that dependencies of $(LOCAL_BUILT_MODULE) (which may include
        # jacoco-report-classes.jar) are copied for every build.
        $(foreach m,$(DEFAULT_DEX_PREOPT_INSTALLED_IMAGE_MODULE) $(2ND_DEFAULT_DEX_PREOPT_INSTALLED_IMAGE_MODULE), \
          $(eval $(call add-dependency,$(firstword $(call module-installed-files,$(m))),$(LOCAL_BUILT_MODULE))) \
        )
      endif
    endif # is_boot_jar

    $(eval $(call copy-one-file,$(LOCAL_SOONG_DEX_JAR),$(common_javalib.jar)))
    $(eval $(call add-dependency,$(LOCAL_BUILT_MODULE),$(common_javalib.jar)))
    ifdef LOCAL_SOONG_CLASSES_JAR
      $(eval $(call add-dependency,$(common_javalib.jar),$(full_classes_jar)))
      ifneq ($(TURBINE_ENABLED),false)
        $(eval $(call add-dependency,$(common_javalib.jar),$(full_classes_header_jar)))
      endif
    endif
  endif

  java-dex : $(LOCAL_BUILT_MODULE)
else  # LOCAL_SOONG_DEX_JAR
  ifndef LOCAL_UNINSTALLABLE_MODULE
    ifndef LOCAL_IS_HOST_MODULE
      $(call pretty-error,Installable device module must have LOCAL_SOONG_DEX_JAR set)
    endif
  endif
endif  # LOCAL_SOONG_DEX_JAR

ALL_MODULES.$(my_register_name).CLASSES_JAR := $(full_classes_jar)

ifdef LOCAL_SOONG_AAR
  ALL_MODULES.$(my_register_name).AAR := $(LOCAL_SOONG_AAR)
endif

# Copy dexpreopt.config files from Soong libraries to the location where Make
# modules can find them.
ifdef LOCAL_SOONG_DEXPREOPT_CONFIG
  $(eval $(call copy-one-file,$(LOCAL_SOONG_DEXPREOPT_CONFIG), $(call local-intermediates-dir,)/dexpreopt.config))
  my_dexpreopt_config := $(PRODUCT_OUT)/dexpreopt_config/$(LOCAL_MODULE)_dexpreopt.config
  $(eval $(call copy-one-file,$(LOCAL_SOONG_DEXPREOPT_CONFIG), $(my_dexpreopt_config)))
  $(LOCAL_BUILT_MODULE): $(my_dexpreopt_config)
endif

ifdef LOCAL_SOONG_CLASSES_JAR
javac-check : $(full_classes_jar)
javac-check-$(LOCAL_MODULE) : $(full_classes_jar)
endif
.PHONY: javac-check-$(LOCAL_MODULE)

ifndef LOCAL_IS_HOST_MODULE
ifeq ($(LOCAL_SDK_VERSION),system_current)
my_link_type := java:system
else ifneq (,$(call has-system-sdk-version,$(LOCAL_SDK_VERSION)))
my_link_type := java:system
else ifeq ($(LOCAL_SDK_VERSION),core_current)
my_link_type := java:core
else ifneq ($(LOCAL_SDK_VERSION),)
my_link_type := java:sdk
else
my_link_type := java:platform
endif
# warn/allowed types are both empty because Soong modules can't depend on
# make-defined modules.
my_warn_types :=
my_allowed_types :=

my_link_deps :=
my_2nd_arch_prefix := $(LOCAL_2ND_ARCH_VAR_PREFIX)
my_common := COMMON
include $(BUILD_SYSTEM)/link_type.mk
endif # !LOCAL_IS_HOST_MODULE

# LOCAL_EXPORT_SDK_LIBRARIES set by soong is written to exported-sdk-libs file
my_exported_sdk_libs_file := $(intermediates.COMMON)/exported-sdk-libs
$(my_exported_sdk_libs_file): PRIVATE_EXPORTED_SDK_LIBS := $(LOCAL_EXPORT_SDK_LIBRARIES)
$(my_exported_sdk_libs_file):
	@echo "Export SDK libs $@"
	$(hide) mkdir -p $(dir $@) && rm -f $@
	$(if $(PRIVATE_EXPORTED_SDK_LIBS),\
		$(hide) echo $(PRIVATE_EXPORTED_SDK_LIBS) | tr ' ' '\n' > $@,\
		$(hide) touch $@)

SOONG_ALREADY_CONV += $(LOCAL_MODULE)

#######################################
# Capture deps added after base_rules.mk
include $(BUILD_NOTICE_FILE)
#######################################
