# Copyright (C) 2020 The Android Open Source Project
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

# `host-unit-tests` shall only include hostside unittest that don't require a device to run. Tests
# included will be run as part of presubmit check.
# To add tests to the suite, do one of the following:
# * For test modules configured with Android.bp, set attribute `test_options: { unit_test: true }`
# * For test modules configured with mk, set `LOCAL_IS_UNIT_TEST := true`
.PHONY: host-unit-tests

intermediates_dir := $(call intermediates-dir-for,PACKAGING,host-unit-tests)
host_unit_tests_zip := $(PRODUCT_OUT)/host-unit-tests.zip

# Filter shared entries between general-tests and device-tests's HOST_SHARED_LIBRARY.FILES,
# to avoid warning about overriding commands.
my_host_shared_lib_entries_for_host_unit_tests := \
  $(filter $(COMPATIBILITY.device-tests.HOST_SHARED_LIBRARY.FILES),\
	  $(COMPATIBILITY.host-unit-tests.HOST_SHARED_LIBRARY.FILES))
my_host_shared_lib_entries_for_host_unit_tests += \
  $(filter $(COMPATIBILITY.general-tests.HOST_SHARED_LIBRARY.FILES),\
	  $(COMPATIBILITY.host-unit-tests.HOST_SHARED_LIBRARY.FILES))
my_host_shared_lib_for_host_unit_tests := $(foreach m,\
  $(my_host_shared_lib_entries_for_host_unit_tests),$(call word-colon,2,$(m)))

my_host_unit_tests_shared_lib_files := \
  $(filter-out $(my_host_shared_lib_entries_for_host_unit_tests),\
	 $(COMPATIBILITY.host-unit-tests.HOST_SHARED_LIBRARY.FILES))

my_host_shared_lib_for_host_unit_tests += $(call copy-many-files,\
  $(my_host_unit_tests_shared_lib_files))

my_symlinks_for_host_unit_tests := $(foreach f,$(COMPATIBILITY.host-unit-tests.SYMLINKS),\
  $(strip $(eval _cmf_tuple := $(subst :, ,$(f))) \
  $(eval _cmf_src := $(word 1,$(_cmf_tuple))) \
  $(eval _cmf_dest := $(word 2,$(_cmf_tuple))) \
  $(call symlink-file,$(_cmf_src),$(_cmf_src),$(_cmf_dest)) \
  $(_cmf_dest)))

$(host_unit_tests_zip) : PRIVATE_HOST_SHARED_LIBS := $(my_host_shared_lib_for_host_unit_tests)

$(host_unit_tests_zip) : PRIVATE_SYMLINKS := $(my_symlinks_for_host_unit_tests)

$(host_unit_tests_zip) : $(COMPATIBILITY.host-unit-tests.FILES) $(my_host_shared_lib_for_host_unit_tests) $(my_symlinks_for_host_unit_tests) $(SOONG_ZIP)
	echo $(sort $(COMPATIBILITY.host-unit-tests.FILES)) | tr " " "\n" > $@.list
	grep $(HOST_OUT_TESTCASES) $@.list > $@-host.list || true
	$(hide) for shared_lib in $(PRIVATE_HOST_SHARED_LIBS); do \
	  echo $$shared_lib >> $@-host.list; \
	done
	$(hide) for symlink in $(PRIVATE_SYMLINKS); do \
    echo $$symlink >> $@-host.list; \
  done
	grep $(TARGET_OUT_TESTCASES) $@.list > $@-target.list || true
	$(SOONG_ZIP) -d -o $@ -P host -C $(HOST_OUT) -l $@-host.list \
	  -P target -C $(PRODUCT_OUT) -l $@-target.list -sha256 -debug
	rm -f $@.list $@-target.list $@-host.list

host-unit-tests: $(host_unit_tests_zip)
$(call dist-for-goals, host-unit-tests, $(host_unit_tests_zip))

$(call declare-1p-container,$(host_unit_tests_zip),)
$(call declare-container-license-deps,$(host_unit_tests_zip),$(COMPATIBILITY.host-unit-tests.FILES) $(my_host_shared_lib_for_host_unit_tests),$(PRODUCT_OUT)/:/)

tests: host-unit-tests
