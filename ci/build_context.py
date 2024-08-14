# Copyright 2024, The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Container class for build context with utility functions."""

import re


class BuildContext:

  def __init__(self, build_context_dict: dict[str, any]):
    self._build_context_dict = build_context_dict

  @classmethod
  def create(cls, build_context_dict: dict[str, any]):
    build_context = cls(build_context_dict)
    build_context._parse_dict()
    return build_context

  def _parse_dict(self):
    self.enabled_build_features = self._build_context_dict.get('enabledBuildFeatures', [])
    self.test_infos = set()
    for test_info_dict in self._build_context_dict.get('testContext', dict()).get('testInfos', []):
      self.test_infos.add(self.TestInfo.create(test_info_dict))

  def build_target_used(self, target: str) -> bool:
    return any(test.build_target_used(target) for test in self.test_infos)

  class TestInfo():

    _DOWNLOAD_OPTS = {
        'test-config-only-zip',
        'test-zip-file-filter',
        'extra-host-shared-lib-zip',
        'sandbox-tests-zips',
        'additional-files-filter',
        'cts-package-name',
    }

    def __init__(self, test_info_dict: dict[str, any]):
      self.test_info_dict = test_info_dict

    @classmethod
    def create(cls, test_info_dict: dict[str, any]):
      test_info = cls(test_info_dict)
      test_info._parse_dict()
      return test_info

    def _parse_dict(self):
      self.is_test_mapping = False
      self.test_mapping_test_groups = set()
      self.file_download_options = set()
      for opt in self.test_info_dict.get('extraOptions', []):
        key = opt.get('key')
        if key == 'test-mapping-test-group':
          self.is_test_mapping = True
          self.test_mapping_test_groups.update(opt.get('values', set()))

        if key in self._DOWNLOAD_OPTS:
          self.file_download_options.update(opt.get('values', set()))

    def build_target_used(self, target: str) -> bool:
      # For all of a targets' outputs, check if any of the regexes used by tests
      # to download artifacts would match it. If any of them do then this target
      # is necessary.
      regex = r'\b(%s)\b' % re.escape(target)
      return any(re.search(regex, opt) for opt in self.file_download_options)
