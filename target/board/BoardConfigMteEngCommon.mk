# BoardConfigMteCommon.mk
#
# Include from BoardConfig.mk to ensure that the board is
# configured properly for MTE in eng builds

ifeq (,$(filter %_fullmte,$(TARGET_PRODUCT)))
  ifneq (,$(filter eng,$(TARGET_BUILD_VARIANT)))
    BOARD_KERNEL_CMDLINE += kasan=off
    ifeq ($(filter memtag_heap,$(SANITIZE_TARGET)),)
      SANITIZE_TARGET := $(strip $(SANITIZE_TARGET) memtag_heap)
    endif
  endif
endif
