
include $(BUILD_SYSTEM)/clang/x86_64.mk
include $(BUILD_SYSTEM)/clang/HOST_x86_common.mk

ifeq ($(HOST_OS),linux)
CLANG_CONFIG_x86_64_HOST_TRIPLE := x86_64-linux-gnu
CLANG_CONFIG_x86_64_HOST_COMBO_EXTRA_ASFLAGS := $(CLANG_CONFIG_x86_LINUX_HOST_EXTRA_ASFLAGS)
CLANG_CONFIG_x86_64_HOST_COMBO_EXTRA_CFLAGS := $(CLANG_CONFIG_x86_LINUX_HOST_EXTRA_CFLAGS)
CLANG_CONFIG_x86_64_HOST_COMBO_EXTRA_CPPFLAGS := $(CLANG_CONFIG_x86_LINUX_HOST_EXTRA_CPPFLAGS)
CLANG_CONFIG_x86_64_HOST_COMBO_EXTRA_LDFLAGS := $(CLANG_CONFIG_x86_LINUX_HOST_EXTRA_LDFLAGS)
endif
ifeq ($(HOST_OS),darwin)
CLANG_CONFIG_x86_64_HOST_TRIPLE := x86_64-apple-darwin
CLANG_CONFIG_x86_64_HOST_COMBO_EXTRA_ASFLAGS := $(CLANG_CONFIG_x86_DARWIN_HOST_EXTRA_ASFLAGS)
CLANG_CONFIG_x86_64_HOST_COMBO_EXTRA_CFLAGS := $(CLANG_CONFIG_x86_DARWIN_HOST_EXTRA_CFLAGS)
CLANG_CONFIG_x86_64_HOST_COMBO_EXTRA_CPPFLAGS := $(CLANG_CONFIG_x86_DARWIN_HOST_EXTRA_CPPFLAGS)
CLANG_CONFIG_x86_64_HOST_COMBO_EXTRA_LDFLAGS := $(CLANG_CONFIG_x86_DARWIN_HOST_EXTRA_LDFLAGS)
endif

CLANG_CONFIG_x86_64_HOST_EXTRA_ASFLAGS := \
  $(CLANG_CONFIG_EXTRA_ASFLAGS) \
  $(CLANG_CONFIG_HOST_EXTRA_ASFLAGS) \
  $(CLANG_CONFIG_x86_64_EXTRA_ASFLAGS) \
  $(CLANG_CONFIG_x86_64_HOST_COMBO_EXTRA_ASFLAGS) \
  -target $(CLANG_CONFIG_x86_64_HOST_TRIPLE)

CLANG_CONFIG_x86_64_HOST_EXTRA_CFLAGS := \
  $(CLANG_CONFIG_EXTRA_CFLAGS) \
  $(CLANG_CONFIG_HOST_EXTRA_CFLAGS) \
  $(CLANG_CONFIG_x86_64_EXTRA_CFLAGS) \
  $(CLANG_CONFIG_x86_64_HOST_COMBO_EXTRA_CFLAGS) \
  $(CLANG_CONFIG_x86_64_HOST_EXTRA_ASFLAGS)

CLANG_CONFIG_x86_64_HOST_EXTRA_CONLYFLAGS := \
  $(CLANG_CONFIG_EXTRA_CONLYFLAGS) \
  $(CLANG_CONFIG_HOST_EXTRA_CONLYFLAGS) \
  $(CLANG_CONFIG_x86_64_EXTRA_CONLYFLAGS) \
  $(CLANG_CONFIG_x86_64_HOST_COMBO_EXTRA_CONLYFLAGS)

CLANG_CONFIG_x86_64_HOST_EXTRA_CPPFLAGS := \
  $(CLANG_CONFIG_EXTRA_CPPFLAGS) \
  $(CLANG_CONFIG_HOST_EXTRA_CPPFLAGS) \
  $(CLANG_CONFIG_x86_64_EXTRA_CPPFLAGS) \
  $(CLANG_CONFIG_x86_64_HOST_COMBO_EXTRA_CPPFLAGS) \
  -target $(CLANG_CONFIG_x86_64_HOST_TRIPLE)

CLANG_CONFIG_x86_64_HOST_EXTRA_LDFLAGS := \
  $(CLANG_CONFIG_EXTRA_LDFLAGS) \
  $(CLANG_CONFIG_HOST_EXTRA_LDFLAGS) \
  $(CLANG_CONFIG_x86_64_EXTRA_LDFLAGS) \
  $(CLANG_CONFIG_x86_64_HOST_COMBO_EXTRA_LDFLAGS) \
  -target $(CLANG_CONFIG_x86_64_HOST_TRIPLE)

define convert-to-host-clang-flags
  $(strip \
  $(call subst-clang-incompatible-x86_64-flags,\
  $(filter-out $(CLANG_CONFIG_x86_64_UNKNOWN_CFLAGS),\
  $(1))))
endef

CLANG_HOST_GLOBAL_CFLAGS := \
  $(call convert-to-host-clang-flags,$(HOST_GLOBAL_CFLAGS)) \
  $(CLANG_CONFIG_x86_64_HOST_EXTRA_CFLAGS)

CLANG_HOST_GLOBAL_CONLYFLAGS := \
  $(call convert-to-host-clang-flags,$(HOST_GLOBAL_CONLYFLAGS)) \
  $(CLANG_CONFIG_x86_64_HOST_EXTRA_CONLYFLAGS)

CLANG_HOST_GLOBAL_CPPFLAGS := \
  $(call convert-to-host-clang-flags,$(HOST_GLOBAL_CPPFLAGS)) \
  $(CLANG_CONFIG_x86_64_HOST_EXTRA_CPPFLAGS)

CLANG_HOST_GLOBAL_LDFLAGS := \
  $(call convert-to-host-clang-flags,$(HOST_GLOBAL_LDFLAGS)) \
  $(CLANG_CONFIG_x86_64_HOST_EXTRA_LDFLAGS)

HOST_LIBPROFILE_RT := $(LLVM_RTLIB_PATH)/libclang_rt.profile-x86_64.a
