ifeq (,$(filter %_fullmte,$(TARGET_PRODUCT)))
ifneq (,$(filter eng,$(TARGET_BUILD_VARIANT)))
PRODUCT_ENG_VARIANT_WITH_MEMTAG ?= true
endif
endif

ifeq ($(PRODUCT_ENG_VARIANT_WITH_MEMTAG),true)
BOARD_KERNEL_CMDLINE += kasan=off
ifeq ($(filter memtag_heap,$(SANITIZE_TARGET)),)
	SANITIZE_TARGET := $(strip $(SANITIZE_TARGET) memtag_heap)
endif
endif
