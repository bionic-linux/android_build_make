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
import re


class OptimizedBuildTarget(ABC):
  """A representation of an optimized build target.

  This class will determine what targets to build given a given build_cotext and
  will have a packaging function to generate any necessary output zips for the
  build.
  """

  def __init__(
      self, target: str, build_context: dict[str, any], args: argparse.Namespace
  ):
    self.target = target
    self.build_context = build_context
    self.args = args

  def get_build_targets(self) -> set[str]:
    if self.get_enabled_flag() in self.build_context.get(
        'enabledBuildFeatures', []
    ):
      return self.get_build_targets_impl()
    return {self.target}

  def package_outputs(self):
    if self.get_enabled_flag() in self.build_context.get(
        'enabledBuildFeatures', []
    ):
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

  def __init__(self, target: str):
    self.target = target

  def get_build_targets(self) -> set[str]:
    return {self.target}

  def package_outputs(self):
    pass


class ExcludeUnusedTargetOptimizer(OptimizedBuildTarget):
  """Optimizer that eliminates the given test suite if its outputs are not downloaded

  by the given ATP test configuration.

  This optimizer will check test args passed in from the build context and not
  build the given suite if its outputs are not downloaded by the given test
  configs.  If the target is used, it will fall back to whatever optimizer is
  passed in.
  """

  _DOWNLOAD_OPTS = {
      'test-config-only-zip',
      'test-zip-file-filter',
      'extra-host-shared-lib-zip',
      'sandbox-tests-zips',
      'additional-files-filter',
      'cts-package-name',
  }

  _TARGET_TO_OUTPUTS = {
      'catbox': ['android-catbox.zip'],
      'gcatbox': ['android-gcatbox.zip'],
  }

  def __init__(
      self,
      target: str,
      build_context: dict[str, any],
      args: argparse.Namespace,
      fallback_optimizer: OptimizedBuildTarget,
      target_to_outputs: dict['str', list['str']] = None,
  ):
    super().__init__(target, build_context, args)
    self.fallback_optimizer = fallback_optimizer
    if not target_to_outputs:
      target_to_outputs = self._TARGET_TO_OUTPUTS
    self.target_to_outputs = target_to_outputs

  def get_build_targets_impl(self) -> set[str]:
    if self._target_outputs_used():
      return self.fallback_optimizer.get_build_targets()

    return set()

  def package_outputs_impl(self):
    if self._target_outputs_used():
      return self.fallback_optimizer.package_outputs()

  def get_enabled_flag(self):
    return f'{self.target}-atp-exclusion'

  def _target_outputs_used(self) -> bool:
    file_download_regexes = self._aggregate_file_download_regexes()
    for artifact in self.target_to_outputs[self.target]:
      for regex in file_download_regexes:
        if re.match(regex, artifact):
          return True
    return False

  def _aggregate_file_download_regexes(self) -> set[re.Pattern]:
    all_regexes = set()
    for test_info in self._get_test_infos():
      for opt in test_info.get('extraOptions', []):
        if opt.get('key', '') in self._DOWNLOAD_OPTS:
          all_regexes.update(
              re.compile(value) for value in opt.get('values', [])
          )
    return all_regexes

  def _get_test_infos(self):
    return self.build_context.get('testContext', dict()).get('testInfos', [])

  @classmethod
  def get_optimized_targets(cls) -> dict[str, OptimizedBuildTarget]:
    optimized_targets = {}
    for target in cls._TARGET_TO_OUTPUTS.keys():
      optimized_targets[target] = functools.partial(
          cls, fallback_optimizer=NullOptimizer(target)
      )

    return optimized_targets


OPTIMIZED_BUILD_TARGETS = {}
OPTIMIZED_BUILD_TARGETS.update(
    ExcludeUnusedTargetOptimizer.get_optimized_targets()
)
