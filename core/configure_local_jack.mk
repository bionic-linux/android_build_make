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

ifdef ANDROID_FORCE_JACK_ENABLED
LOCAL_JACK_ENABLED := $(ANDROID_FORCE_JACK_ENABLED)
endif

LOCAL_JACK_ENABLED := $(strip $(LOCAL_JACK_ENABLED))
LOCAL_MODULE := $(strip $(LOCAL_MODULE))

valid_jack_enabled_values := full incremental javac_frontend disabled

ifdef LOCAL_JACK_ENABLED
  ifneq ($(LOCAL_JACK_ENABLED),$(filter $(firstword $(LOCAL_JACK_ENABLED)),$(valid_jack_enabled_values)))
    $(error $(LOCAL_PATH): invalid LOCAL_JACK_ENABLED "$(LOCAL_JACK_ENABLED)" for $(LOCAL_MODULE))
  endif

  ifeq ($(LOCAL_JACK_ENABLED),disabled)
    LOCAL_JACK_ENABLED := disabled
  endif
endif

ifdef $(LOCAL_MODULE).JACK_VERSION
LOCAL_JACK_VERSION := $($(LOCAL_MODULE).JACK_VERSION)
else
LOCAL_JACK_VERSION := $(JACK_DEFAULT_VERSION)
endif
