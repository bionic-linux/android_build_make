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

$(call record-module-type,HOST_PREBUILT)
$(if $(my_register_name),$(eval ALL_MODULES.$(my_register_name).MAKE_MODULE_TYPE:=HOST_PREBUILT))

LOCAL_IS_HOST_MODULE := true
include $(BUILD_MULTI_PREBUILT)
