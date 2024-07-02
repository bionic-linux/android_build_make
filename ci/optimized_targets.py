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
    features = self.build_context.get('enabledBuildFeatures', [])
    if self.get_enabled_flag() in features:
      return self.get_build_targets_impl()
    return {self.target}

  def package_outputs(self):
    features = self.build_context.get('enabledBuildFeatures', [])
    if self.get_enabled_flag() in features:
      self.package_outputs_impl()

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

  _OPTIMIZED_TARGETS = {
      'catbox',
      'gcatbox',
  }

  def __init__(
      self,
      target: str,
      build_context: dict[str, any],
      args: argparse.Namespace,
      fallback_optimizer: OptimizedBuildTarget,
      optimized_targets: set['str'] = None,
  ):
    super().__init__(target, build_context, args)
    self.fallback_optimizer = fallback_optimizer
    if not optimized_targets:
      optimized_targets = self._OPTIMIZED_TARGETS
    self.optimized_targets = optimized_targets

  def get_build_targets_impl(self) -> set[str]:
    if self._target_outputs_used():
      return self.fallback_optimizer.get_build_targets()

    return set()

  def package_outputs_impl(self):
    if self._target_outputs_used():
      return self.fallback_optimizer.package_outputs()

  def get_enabled_flag(self):
    return f'{self.target}_atp_exclusion'

  def _target_outputs_used(self) -> bool:
    """Determines whether this target's outputs are used by the test configurations listed in the build context."""
    file_download_regexes = self._aggregate_file_download_regexes()
    # For all of a targets' outputs, check if any of the regexes used by tests
    # to download artifacts would match it. If any of them do then this target
    # is necessary.
    for artifact in self._get_target_potential_outputs(self.target):
      for regex in file_download_regexes:
        if re.match(regex, artifact):
          return True
    return False

  def _get_target_potential_outputs(self, target: str) -> set[str]:
    tests_suffix = '-tests'
    if target.endswith('tests'):
      tests_suffix = ''
    # This is an approximate list of all the outputs a typical test suite target
    # may have, and is the basis for what we compare a test's artifact download
    # regex to.
    return {
        f'{target}.zip',
        f'android-{target}.zip',
        f'android-{target}-verifier.zip',
        f'{target}{tests_suffix}_list.zip',
        f'android-{target}{tests_suffix}_list.zip',
        f'{target}{tests_suffix}_host-shared-libs.zip',
        f'android-{target}{tests_suffix}_host-shared-libs.zip',
        f'{target}{tests_suffix}_configs.zip',
        f'android-{target}{tests_suffix}_configs.zip',
    }

  def _aggregate_file_download_regexes(self) -> set[re.Pattern]:
    """Lists out all test config options to specify targets to download.

    These come in the form of regexes.
    """
    all_regexes = set()
    for test_info in self._get_test_infos():
      for opt in test_info.get('extraOptions', []):
        # check the known list of options for downloading files.
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
    for target in cls._OPTIMIZED_TARGETS:
      optimized_targets[target] = functools.partial(
          cls, fallback_optimizer=NullOptimizer(target)
      )

    return optimized_targets


OPTIMIZED_BUILD_TARGETS = ExcludeUnusedTargetOptimizer.get_optimized_targets()
