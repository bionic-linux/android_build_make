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

"""Utility functions for build_test_suites."""

import re

DOWNLOAD_OPTS = {
    'test-config-only-zip',
    'test-zip-file-filter',
    'extra-host-shared-lib-zip',
    'sandbox-tests-zips',
    'additional-files-filter',
    'cts-package-name',
}


def aggregate_file_download_options(build_context: dict[str, any]) -> set[str]:
  """Lists out all test config options to specify targets to download.

  These come in the form of regexes.
  """
  all_options = set()
  for test_info in build_context.get('testContext', dict()).get(
      'testInfos', []
  ):
    for opt in test_info.get('extraOptions', []):
      # check the known list of options for downloading files.
      if opt.get('key') in DOWNLOAD_OPTS:
        all_options.update(opt.get('values', []))
  return all_options


def build_target_used(target: str, file_download_options: set[str]) -> bool:
  """Determines whether this target's outputs are used by the test configurations listed in the build context."""
  # For all of a targets' outputs, check if any of the regexes used by tests
  # to download artifacts would match it. If any of them do then this target
  # is necessary.
  regex = r'\b(%s)\b' % re.escape(target)
  return any(re.search(regex, opt) for opt in file_download_options)
