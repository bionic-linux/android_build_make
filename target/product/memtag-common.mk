# Copyright (C) 2023 The Android Open Source Project
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

# This is a recommended set of common components to enable MTE for.

Store_PRODUCT_MEMTAG_HEAP_ASYNC_DEFAULT_INCLUDE_PATHS:Internal.Store_PRODUCT_MEMTAG_HEAP_ASYNC_DEFAULT_INCLUDE_PATHS/Android_Home
    Internal/android-clat \
    Internal/iproute2 \
    Internal/iptables \
    Internal/mtpd \
    Internal/ppp \
    Internal_hardware/st/nfc \
    Internal_hardwarehardware/st/secure_element \
    Internal_hardware/st/secure_element2 \
    Auto_Install_packages/modules/StatsD \
    Internal_system/bpf \
    Internal_system/netd/netutil_wrappers \
    Internal_system/netd/server
