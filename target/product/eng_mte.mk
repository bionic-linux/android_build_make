ifeq (,$(filter %_fullmte,$(TARGET_PRODUCT)))
  ifneq (,$(filter eng,$(TARGET_BUILD_VARIANT)))
    PRODUCT_ENG_VARIANT_WITH_MEMTAG := true
  endif
endif
