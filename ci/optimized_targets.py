#
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

from abc import ABC
import argparse
import functools
import json
import logging
import os
from typing import Self

import build_context
import test_mapping_module_retriever


class OptimizedBuildTarget(ABC):
  """A representation of an optimized build target.

  This class will determine what targets to build given a given build_cotext and
  will have a packaging function to generate any necessary output zips for the
  build.
  """

  def __init__(
      self,
      target: str,
      build_context: build_context.BuildContext,
      args: argparse.Namespace,
  ):
    self.target = target
    self.build_context = build_context
    self.args = args

  def get_build_targets(self) -> set[str]:
    features = self.build_context.enabled_build_features
    if self.get_enabled_flag() in features:
      self.modules_to_build = self.get_build_targets_impl()
      return self.modules_to_build

    self.modules_to_build = {self.target}
    return {self.target}

  def package_outputs(self):
    features = self.build_context.enabled_build_features
    if self.get_enabled_flag() in features:
      return self.package_outputs_impl()

  def package_outputs_impl(self):
    raise NotImplementedError(
        f'package_outputs_impl not implemented in {type(self).__name__}'
    )

  def get_enabled_flag(self):
    raise NotImplementedError(
        f'get_enabled_flag not implemented in {type(self).__name__}'
    )

  def get_build_targets_impl(self) -> set[str]:
    raise NotImplementedError(
        f'get_build_targets_impl not implemented in {type(self).__name__}'
    )


class NullOptimizer(OptimizedBuildTarget):
  """No-op target optimizer.

  This will simply build the same target it was given and do nothing for the
  packaging step.
  """

  def __init__(self, target):
    self.target = target

  def get_build_targets(self):
    return {self.target}

  def package_outputs(self):
    pass


class ChangeInfo:

  def __init__(self, change_info_file_path):
    self._change_info_file_path = change_info_file_path

  @classmethod
  def create(cls, change_info_file_path):
    change_info = cls(change_info_file_path)
    change_info._parse_change_info_file()
    return change_info

  def _parse_change_info_file(self):
    try:
      with open(self._change_info_file_path) as change_info_file:
        change_info_contents = json.load(change_info_file)
    except json.decoder.JSONDecodeError:
      logging.error(f'Failed to load CHANGE_INFO: {self._change_info_file_path}')
      raise

    self._change_info_contents = change_info_contents

  def find_changed_files(self) -> set[str]:
    changed_files = set()

    for change in self._change_info_contents['changes']:
      project_path = change.get('projectPath') + '/'

      for revision in change.get('revisions'):
        for file_info in revision.get('fileInfos'):
          changed_files.add(project_path + file_info.get('path'))

    return changed_files

class GeneralTestsOptimizer(OptimizedBuildTarget):
  """general-tests optimizer

  TODO(b/358215235): Implement

  This optimizer reads in the list of changed files from the file located in
  env[CHANGE_INFO] and uses this list alongside the normal TEST MAPPING logic to
  determine what test mapping modules will run for the given changes. It then
  builds those modules and packages them in the same way general-tests.zip is
  normally built.
  """

  # List of modules that are always required to be in general-tests.zip.
  # soong_zip isn't required to be in general-tests but is required to zip it up
  # at the end.
  _REQUIRED_MODULES = frozenset(
      ['cts-tradefed', 'vts-tradefed', 'compatibility-host-util', 'soong_zip']
  )

  def get_build_targets_impl(self) -> set[str]:
    change_info_file_path = os.environ.get('CHANGE_INFO')
    if not change_info_file_path:
      logging.info(
          'No CHANGE_INFO env var found, general-tests optimization disabled.'
      )
      return {'general-tests'}

    test_infos = self.build_context.test_infos
    test_mapping_test_groups = set()
    for test_info in test_infos:
      is_test_mapping = test_info.is_test_mapping
      current_test_mapping_test_groups = test_info.test_mapping_test_groups
      uses_general_tests = test_info.build_target_used('general-tests')

      if uses_general_tests and not is_test_mapping:
        logging.info(
            'Test uses general-tests.zip but is not test-mapping, general-tests'
            ' optimization disabled.'
        )
        return {'general-tests'}

      if is_test_mapping:
        test_mapping_test_groups.update(current_test_mapping_test_groups)

    change_info = ChangeInfo.create(change_info_file_path)
    changed_files = change_info.find_changed_files()

    test_mappings = test_mapping_module_retriever.GetTestMappings(
        changed_files, set()
    )

    modules_to_build = set(self._REQUIRED_MODULES)

    modules_to_build.update(
        self._find_affected_modules(
            test_mappings, changed_files, test_mapping_test_groups
        )
    )

    return modules_to_build


  def _find_affected_modules(
      self,
      test_mappings: dict[str, any],
      changed_files: set[str],
      test_mapping_test_groups: set[str],
  ) -> set[str]:
    modules = set()

    # The test_mappings object returned by GetTestMappings is organized as
    # follows:
    # {
    #   'test_mapping_file_path': {
    #     'group_name' : [
    #       'name': 'module_name',
    #     ],
    #   }
    # }
    for test_mapping in test_mappings.values():
      for group_name, group in test_mapping.items():
        # If a module is not in any of the test mapping groups being tested skip
        # it.
        if group_name not in test_mapping_test_groups:
          continue

        for entry in group:
          module_name = entry.get('name', None)

          if not module_name:
            continue

          file_patterns = entry.get('file_patterns', '')
          if not file_patterns:
            modules.add(module_name)
            continue

          if self._matches_file_patterns(file_patterns, changed_files):
            modules.add(module_name)
            continue

    return modules

  # TODO(lucafarsi): Share this logic with the original logic in
  # test_mapping_test_retriever.py
  def _matches_file_patterns(
      self, file_patterns: list[set], changed_files: set[str]
  ) -> bool:
    for changed_file in changed_files:
      for pattern in file_patterns:
        if re.search(pattern, changed_file):
          return True

    return False

  def get_enabled_flag(self):
    return 'general_tests_optimized'

  @classmethod
  def get_optimized_targets(cls) -> dict[str, OptimizedBuildTarget]:
    return {'general-tests': functools.partial(cls)}


OPTIMIZED_BUILD_TARGETS = {}
OPTIMIZED_BUILD_TARGETS.update(GeneralTestsOptimizer.get_optimized_targets())
