#
# Copyright (C) 2008 The Android Open Source Project
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
#

#
# Standard rules for building a host java library.
#

LOCAL_MODULE_CLASS := JAVA_LIBRARIES
LOCAL_MODULE_SUFFIX := $(COMMON_JAVA_PACKAGE_SUFFIX)
LOCAL_IS_HOST_MODULE := true
LOCAL_BUILT_MODULE_STEM := javalib.jar

include $(BUILD_SYSTEM)/base_rules.mk

# Make sure overridecheck is built before any other java.
ifeq ($(LOCAL_MODULE),overridecheck)
overridecheck_dependency :=
else
overridecheck_dependency := $(OVERRIDECHECK)
endif

$(LOCAL_BUILT_MODULE): $(java_sources) $(java_resource_sources) $(full_java_lib_deps) | $(overridecheck_dependency)
	$(transform-host-java-to-package)
