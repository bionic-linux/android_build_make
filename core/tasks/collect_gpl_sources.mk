# Copyright (C) 2011 The Android Open Source Project
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

# The rule below doesn't have dependenices on the files that it copies,
# so manually generate into a PACKAGING intermediate dir, which is wiped
# in installclean between incremental builds on build servers.
gpl_source_tgz := $(call intermediates-dir-for,PACKAGING,gpl_source)/gpl_source.tgz

$(gpl_source_tgz): PRIVATE_GPL_MODULES := $(sort $(call find-restricted-modules))
$(gpl_source_tgz): PRIVATE_GPL_PATHS := $(sort $(patsubst %/, %, $(sort $(foreach m, $(PRIVATE_GPL_MODULES), $(ALL_MODULES.$(m).PATH)))))
$(gpl_source_tgz): PRIVATE_GPL_SOURCE := $(call all-files-under, $(PRIVATE_GPL_PATHS))
$(gpl_source_tgz) : $(PRIVATE_GPL_SOURCE)
	@echo Package GPL sources: $@
	$(hide) tar cfz $@ --exclude ".git*" $(PRIVATE_GPL_PATHS)

# Dist the tgz only if we are doing a full build
$(call dist-for-goals,droidcore,$(gpl_source_tgz))
