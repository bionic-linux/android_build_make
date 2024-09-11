# Copyright (C) 2024 The Android Open Source Project
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


.PHONY: device-tests-shared-libs

device-tests-shared-libs-zip := $(PRODUCT_OUT)/device-tests_host-shared-libs.zip
my_host_shared_lib_for_device_tests := $(call copy-many-files,$(COMPATIBILITY.device-tests.HOST_SHARED_LIBRARY.FILES))

$(device-tests-shared-libs-zip) : PRIVATE_device_host_shared_libs_zip := $(device-tests-shared-libs-zip)
$(device-tests-shared-libs-zip) : PRIVATE_HOST_SHARED_LIBS := $(my_host_shared_lib_for_device_tests)
$(device-tests-shared-libs-zip) : $(my_host_shared_lib_for_device_tests) $(SOONG_ZIP)
	rm -f $@-shared-libs.list
	$(hide) for shared_lib in $(PRIVATE_HOST_SHARED_LIBS); do \
	  echo $$shared_lib >> $@-host.list; \
	  echo $$shared_lib >> $@-shared-libs.list; \
	done
	grep $(HOST_OUT_TESTCASES) $@-shared-libs.list > $@-host-shared-libs.list || true
	$(SOONG_ZIP) -d -o $(PRIVATE_device_host_shared_libs_zip) \
	  -P host -C $(HOST_OUT) -l $@-host-shared-libs.list

device-tests-shared-libs: $(device-tests-shared-libs-zip)
$(call dist-for-goals, device-tests-shared-libs, $(device-tests-shared-libs-zip))

$(call declare-1p-container,$(device-tests-shared-libs-zip),)
$(call declare-container-license-deps,$(device-tests-shared-libs-zip),$(my_host_shared_lib_for_device_tests),$(PRODUCT_OUT)/:/)

device-tests-shared-libs-zip :=
