#
# Copyright (C) 2018 The Android Open Source Project
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

# Base modules and settings for the system partition.
PRODUCT_PACKAGES += \
    adbd_system_api \
    android.hidl.allocator@1.0-service \
    android.hidl.memory@1.0-impl \
    android.hidl.memory@1.0-impl.vendor \
    android.system.suspend@1.0-service \
    apexd \
    appops \
    atrace \
    audioserver \
    bcc \
    blank_screen \
    blkid \
    bootstat \
    boringssl_self_test \
    bpfloader \
    bugreport \
    bugreportz \
    cgroups.json \
    charger \
    cmd \
    com.android.adbd \
    com.android.i18n \
    com.android.media.swcodec \
    com.android.os.statsd \
    com.android.resolv \
    com.android.runtime \
    com.android.tethering \
    com.android.tzdata \
    debuggerd\
    device_config \
    dmctl \
    dnsmasq \
    dmesgd \
    dpm \
    dump.erofs \
    dumpstate \
    dumpsys \
    e2fsck \
    flags_health_check \
    fsck.erofs \
    fsck_msdos \
    fsverity-release-cert-der \
    fs_config_files_system \
    fs_config_dirs_system \
    group_system \
    gsid \
    gsi_tool \
    heapprofd \
    heapprofd_client \
    gatekeeperd \
    hwservicemanager \
    idmap2 \
    idmap2d \
    incident \
    incidentd \
    incident_helper \
    init.environ.rc \
    init_system \
    input \
    installd \
    ip \
    iptables \
    ip-up-vpn \
    keystore2 \
    credstore \
    ld.mc \
    libaaudio \
    libamidi \
    libandroid \
    libandroidfw \
    libandroid_servers \
    libartpalette-system \
    libbinder \
    libbinder_ndk \
    libbinder_rpc_unstable \
    libc.bootstrap \
    libcamera2ndk \
    libcutils \
    libdl.bootstrap \
    libdl_android.bootstrap \
    libdrmframework \
    libEGL \
    libETC1 \
    libfdtrack \
    libFFTEm \
    libfilterfw \
    libgatekeeper \
    libGLESv1_CM \
    libGLESv2 \
    libGLESv3 \
    libgui \
    libhardware \
    libhardware_legacy \
    libincident \
    libinput \
    libinputflinger \
    libiprouteutil \
    libjpeg \
    liblog \
    libm.bootstrap \
    libmdnssd \
    libmedia \
    libmediandk \
    libmtp \
    libnetd_client \
    libnetlink \
    libnetutils \
    libOpenMAXAL \
    libOpenSLES \
    libpdfium \
    libpixman \
    libpower \
    libpowermanager \
    libradio_metadata \
    libsensorservice \
    libsfplugin_ccodec \
    libsonic \
    libsonivox \
    libsoundpool \
    libspeexresampler \
    libsqlite \
    libstagefright \
    libstagefright_foundation \
    libstagefright_omx \
    libstdc++ \
    libsysutils \
    libui \
    libusbhost \
    libutils \
    libvulkan \
    libwilhelm \
    linker \
    linkerconfig \
    llkd \
    lmkd \
    logcat \
    logd \
    lpdump \
    lshal \
    mdnsd \
    mediacodec.policy \
    mediametrics \
    media_profiles_V1_0.dtd \
    mediaserver \
    mke2fs \
    mkfs.erofs \
    mtpd \
    ndc \
    netd \
    odsign \
    otacerts \
    passwd_system \
    perfetto \
    ping \
    ping6 \
    platform.xml \
    pm \
    pppd \
    prng_seeder \
    racoon \
    recovery-persist \
    resize2fs \
    rss_hwm_reset \
    run-as \
    sanitizer.libraries.txt \
    schedtest \
    screencap \
    sdcard \
    secdiscard \
    selinux_policy_system \
    sensorservice \
    service \
    servicemanager \
    settings \
    sgdisk \
    shell_and_utilities_system \
    snapshotctl \
    snapuserd \
    storaged \
    surfaceflinger \
    task_profiles.json \
    tc \
    tombstoned \
    traced \
    traced_probes \
    tune2fs \
    tzdatacheck \
    uncrypt \
    usbd \
    vdc \
    viewcompiler \
    vold \
    watchdogd \
    wificond \
    wifi.rc \
    wm \

# VINTF data for system image
PRODUCT_PACKAGES += \
    system_manifest.xml \
    system_compatibility_matrix.xml \

# HWASAN runtime for SANITIZE_TARGET=hwaddress builds
ifneq (,$(filter hwaddress,$(SANITIZE_TARGET)))
  PRODUCT_PACKAGES += \
   libclang_rt.hwasan.bootstrap
endif

# Host tools to install
PRODUCT_HOST_PACKAGES += \
    BugReport \
    adb \
    art-tools \
    atest \
    bcc \
    bit \
    dump.erofs \
    e2fsck \
    fastboot \
    flags_health_check \
    fsck.erofs \
    icu-data_host_i18n_apex \
    icu_tzdata.dat_host_tzdata_apex \
    idmap2 \
    incident_report \
    ld.mc \
    lpdump \
    minigzip \
    mke2fs \
    mkfs.erofs \
    resize2fs \
    sgdisk \
    sqlite3 \
    tinyplay \
    tune2fs \
    tzdatacheck \
    unwind_info \
    unwind_reg_info \
    unwind_symbols \
    viewcompiler \
    tzdata_host \
    tzdata_host_tzdata_apex \
    tzlookup.xml_host_tzdata_apex \
    tz_version_host \
    tz_version_host_tzdata_apex \


PRODUCT_COPY_FILES += \
    system/core/rootdir/init.usb.rc:system/etc/init/hw/init.usb.rc \
    system/core/rootdir/init.usb.configfs.rc:system/etc/init/hw/init.usb.configfs.rc \
    system/core/rootdir/etc/hosts:system/etc/hosts

PRODUCT_COPY_FILES += system/core/rootdir/init.no_zygote.rc:system/etc/init/hw/init.no_zygote.rc
PRODUCT_VENDOR_PROPERTIES += ro.zygote?=no_zygote

PRODUCT_SYSTEM_PROPERTIES += debug.atrace.tags.enableflags=0
PRODUCT_SYSTEM_PROPERTIES += persist.traced.enable=1

# Packages included only for eng or userdebug builds, previously debug tagged
PRODUCT_PACKAGES_DEBUG := \
    adb_keys \
    arping \
    dmuserd \
    idlcli \
    init-debug.rc \
    iotop \
    iperf3 \
    iw \
    logpersist.start \
    logtagd.rc \
    procrank \
    profcollectd \
    profcollectctl \
    remount \
    servicedispatcher \
    showmap \
    sqlite3 \
    ss \
    strace \
    su \
    sanitizer-status \
    tracepath \
    tracepath6 \
    traceroute6 \
    unwind_info \
    unwind_reg_info \
    unwind_symbols \

# The set of packages whose code can be loaded by the system server.
PRODUCT_SYSTEM_SERVER_APPS += \
    SettingsProvider \
    WallpaperBackup

PRODUCT_PACKAGES_DEBUG_JAVA_COVERAGE := \
    libdumpcoverage

PRODUCT_COPY_FILES += $(call add-to-product-copy-files-if-exists,\
    frameworks/base/config/preloaded-classes:system/etc/preloaded-classes)

# Note: it is acceptable to not have a dirty-image-objects file. In that case, the special bin
#       for known dirty objects in the image will be empty.
PRODUCT_COPY_FILES += $(call add-to-product-copy-files-if-exists,\
    frameworks/base/config/dirty-image-objects:system/etc/dirty-image-objects)

