
include $(BUILD_SYSTEM)/clang/x86.mk

CLANG_CONFIG_x86_HOST_CROSS_TRIPLE := i686-pc-mingw32

CLANG_CONFIG_x86_HOST_CROSS_EXTRA_ASFLAGS := \
  $(CLANG_CONFIG_EXTRA_ASFLAGS) \
  $(CLANG_CONFIG_HOST_CROSS_EXTRA_ASFLAGS) \
  $(CLANG_CONFIG_x86_EXTRA_ASFLAGS) \
  $(CLANG_CONFIG_x86_HOST_CROSS_COMBO_EXTRA_ASFLAGS) \
  -target $(CLANG_CONFIG_x86_HOST_CROSS_TRIPLE)

CLANG_CONFIG_x86_HOST_CROSS_EXTRA_CFLAGS := \
  $(CLANG_CONFIG_EXTRA_CFLAGS) \
  $(CLANG_CONFIG_HOST_CROSS_EXTRA_CFLAGS) \
  $(CLANG_CONFIG_x86_EXTRA_CFLAGS) \
  $(CLANG_CONFIG_x86_HOST_CROSS_COMBO_EXTRA_CFLAGS) \
  $(CLANG_CONFIG_x86_HOST_CROSS_EXTRA_ASFLAGS)

CLANG_CONFIG_x86_HOST_CROSS_EXTRA_CONLYFLAGS := \
  $(CLANG_CONFIG_EXTRA_CONLYFLAGS) \
  $(CLANG_CONFIG_HOST_CROSS_EXTRA_CONLYFLAGS) \
  $(CLANG_CONFIG_x86_EXTRA_CONLYFLAGS) \
  $(CLANG_CONFIG_x86_HOST_CROSS_COMBO_EXTRA_CONLYFLAGS)

CLANG_CONFIG_x86_HOST_CROSS_EXTRA_CPPFLAGS := \
  $(CLANG_CONFIG_EXTRA_CPPFLAGS) \
  $(CLANG_CONFIG_HOST_CROSS_EXTRA_CPPFLAGS) \
  $(CLANG_CONFIG_x86_EXTRA_CPPFLAGS) \
  $(CLANG_CONFIG_x86_HOST_CROSS_COMBO_EXTRA_CPPFLAGS) \
  -target $(CLANG_CONFIG_x86_HOST_CROSS_TRIPLE)

CLANG_CONFIG_x86_HOST_CROSS_EXTRA_LDFLAGS := \
  $(CLANG_CONFIG_EXTRA_LDFLAGS) \
  $(CLANG_CONFIG_HOST_CROSS_EXTRA_LDFLAGS) \
  $(CLANG_CONFIG_x86_EXTRA_LDFLAGS) \
  $(CLANG_CONFIG_x86_HOST_CROSS_COMBO_EXTRA_LDFLAGS) \
  -target $(CLANG_CONFIG_x86_HOST_CROSS_TRIPLE)

define convert-to-host-win-clang-flags
  $(strip \
  $(call subst-clang-incompatible-x86-flags,\
  $(filter-out $(CLANG_CONFIG_x86_UNKNOWN_CFLAGS),\
  $(1))))
endef

CLANG_HOST_CROSS_GLOBAL_CFLAGS := \
  $(call convert-to-host-clang-flags,$(HOST_CROSS_GLOBAL_CFLAGS)) \
  $(CLANG_CONFIG_x86_HOST_CROSS_EXTRA_CFLAGS)

CLANG_HOST_CROSS_GLOBAL_CONLYFLAGS := \
  $(call convert-to-host-clang-flags,$(HOST_CROSS_GLOBAL_CONLYFLAGS)) \
  $(CLANG_CONFIG_x86_HOST_CROSS_EXTRA_CONLYFLAGS)

CLANG_HOST_CROSS_GLOBAL_CPPFLAGS := \
  $(call convert-to-host-clang-flags,$(HOST_CROSS_GLOBAL_CPPFLAGS)) \
  $(CLANG_CONFIG_x86_HOST_CROSS_EXTRA_CPPFLAGS)

CLANG_HOST_CROSS_GLOBAL_LDFLAGS := \
  $(call convert-to-host-clang-flags,$(HOST_CROSS_GLOBAL_LDFLAGS)) \
  $(CLANG_CONFIG_x86_HOST_CROSS_EXTRA_LDFLAGS)

HOST_CROSS_LIBPROFILE_RT := $(LLVM_RTLIB_PATH)/libclang_rt.profile-i686.a
