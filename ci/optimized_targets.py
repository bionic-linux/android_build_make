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
from build_context import BuildContext
import json
import logging
import pathlib
import os
import subprocess
from typing import Self, Callable, TextIO

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
      build_context: BuildContext,
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

  def get_package_outputs_commands(self) -> list[list[str]]:
    features = self.build_context.enabled_build_features
    if self.get_enabled_flag() in features:
      return self.get_package_outputs_commands_impl()

    return set()

  def get_package_outputs_commands_impl(self) -> set[list[str]]:
    raise NotImplementedError(
        f'get_package_outputs_commands_impl not implemented in {type(self).__name__}'
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

  def get_package_outputs_commands(self):
    return set()


class ChangeInfo:

  def __init__(self, change_info_file_path):
    try:
      with open(change_info_file_path) as change_info_file:
        change_info_contents = json.load(change_info_file)
    except json.decoder.JSONDecodeError:
      logging.error(f'Failed to load CHANGE_INFO: {change_info_file_path}')
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
  _REQUIRED_MODULES = frozenset(
      ['cts-tradefed', 'vts-tradefed', 'compatibility-host-util']
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

    change_info = ChangeInfo(change_info_file_path)
    changed_files = change_info.find_changed_files()

    test_mappings = test_mapping_module_retriever.GetTestMappings(
        changed_files, set()
    )

    modules_to_build = set(self._REQUIRED_MODULES)

    modules_to_build.update(
        test_mapping_module_retriever.FindAffectedModules(
            test_mappings, changed_files, test_mapping_test_groups
        )
    )

    return modules_to_build

  def get_package_outputs_commands_impl(self):
    src_top = os.environ.get('TOP', os.getcwd())
    dist_dir = os.environ.get('DIST_DIR')

    soong_vars = self._get_soong_vars(src_top, ['HOST_OUT_TESTCASES', 'TARGET_OUT_TESTCASES', 'PRODUCT_OUT', 'SOONG_HOST_OUT', 'HOST_OUT'])
    host_out_testcases = pathlib.Path(soong_vars.get('HOST_OUT_TESTCASES'))
    target_out_testcases = pathlib.Path(soong_vars.get('TARGET_OUT_TESTCASES'))
    product_out = pathlib.Path(soong_vars.get('PRODUCT_OUT'))
    soong_host_out = pathlib.Path(soong_vars.get('SOONG_HOST_OUT'))
    host_out = pathlib.Path(soong_vars.get('HOST_OUT'))

    host_paths = []
    target_paths = []
    host_config_files = []
    target_config_files = []
    for module in self.modules_to_build:
      host_path = os.path.join(host_out_testcases, module)
      if os.path.exists(host_path):
        host_paths.append(host_path)
        self._collect_config_files(src_top, host_path, host_config_files)

      target_path = os.path.join(target_out_testcases, module)
      if os.path.exists(target_path):
        target_paths.append(target_path)
        self._collect_config_files(src_top, target_path, target_config_files)

    zip_commands = []

    zip_commands.extend(self._get_zip_test_configs_zips_commands(
        dist_dir, host_out, product_out, host_config_files, target_config_files
    ))

    zip_command = self._base_zip_command(host_out, dist_dir, 'general-tests.zip')

    # Add host testcases.
    zip_command.append('-C')
    zip_command.append(str(os.path.join(src_top, soong_host_out)))
    zip_command.append('-P')
    zip_command.append('host/')
    for path in host_paths:
      zip_command.append('-D')
      zip_command.append(str(path))

    # Add target testcases.
    zip_command.append('-C')
    zip_command.append(str(os.path.join(src_top, product_out)))
    zip_command.append('-P')
    zip_command.append('target')
    for path in target_paths:
      zip_command.append('-D')
      zip_command.append(str(path))

    # TODO(lucafarsi): Push this logic into a general-tests-minimal build command
    # Add necessary tools. These are also hardcoded in general-tests.mk.
    framework_path = os.path.join(soong_host_out, 'framework')

    zip_command.append('-C')
    zip_command.append(str(framework_path))
    zip_command.append('-P')
    zip_command.append('host/tools')
    zip_command.append('-f')
    zip_command.append(str(os.path.join(framework_path, 'cts-tradefed.jar')))
    zip_command.append('-f')
    zip_command.append(
        str(os.path.join(framework_path, 'compatibility-host-util.jar'))
    )
    zip_command.append('-f')
    zip_command.append(str(os.path.join(framework_path, 'vts-tradefed.jar')))

    zip_commands.append(zip_command)
    return zip_commands


  def _collect_config_files(
      self, src_top: pathlib.Path, root_dir: pathlib.Path, config_files: list[str]
  ):
    for root, dirs, files in os.walk(os.path.join(src_top, root_dir)):
      for file in files:
        if file.endswith('.config'):
          config_files.append(os.path.join(root_dir, file))


  def _base_zip_command(
      self, src_top: pathlib.Path, dist_dir: pathlib.Path, name: str
  ) -> list[str]:
    return [
        str(os.path.join(src_top, 'prebuilts', 'build-tools', 'linux-x86', 'bin', 'soong_zip')),
        '-d',
        '-o',
        str(os.path.join(dist_dir, name)),
    ]


  # generate general-tests_configs.zip which contains all of the .config files
  # that were built and general-tests_list.zip which contains a text file which
  # lists all of the .config files that are in general-tests_configs.zip.
  #
  # general-tests_comfigs.zip is organized as follows:
  # /
  #   host/
  #     testcases/
  #       test_1.config
  #       test_2.config
  #       ...
  #   target/
  #     testcases/
  #       test_1.config
  #       test_2.config
  #       ...
  #
  # So the process is we write out the paths to all the host config files into one
  # file and all the paths to the target config files in another. We also write
  # the paths to all the config files into a third file to use for
  # general-tests_list.zip.
  def _get_zip_test_configs_zips_commands(
      self,
      dist_dir: pathlib.Path,
      host_out: pathlib.Path,
      product_out: pathlib.Path,
      host_config_files: list[str],
      target_config_files: list[str],
  ) -> list[list[str]]:
    with open(
        os.path.join(host_out, 'host_general-tests_list'), 'w'
    ) as host_list_file, open(
        os.path.join(product_out, 'target_general-tests_list'), 'w'
    ) as target_list_file, open(
        os.path.join(host_out, 'general-tests_list'), 'w'
    ) as list_file:

      for config_file in host_config_files:
        host_list_file.write(config_file + '\n')
        list_file.write('host/' + os.path.relpath(config_file, host_out) + '\n')

      for config_file in target_config_files:
        target_list_file.write(config_file + '\n')
        list_file.write(
            'target/' + os.path.relpath(config_file, product_out) + '\n'
        )

    zip_commands = []

    tests_config_zip_command = self._base_zip_command(
        host_out, dist_dir, 'general-tests_configs.zip'
    )
    tests_config_zip_command.append('-P')
    tests_config_zip_command.append('host')
    tests_config_zip_command.append('-C')
    tests_config_zip_command.append(str(host_out))
    tests_config_zip_command.append('-l')
    tests_config_zip_command.append(
        str(os.path.join(host_out, 'host_general-tests_list'))
    )
    tests_config_zip_command.append('-P')
    tests_config_zip_command.append('target')
    tests_config_zip_command.append('-C')
    tests_config_zip_command.append(str(product_out))
    tests_config_zip_command.append('-l')
    tests_config_zip_command.append(
        str(os.path.join(product_out, 'target_general-tests_list'))
    )
    zip_commands.append(tests_config_zip_command)

    tests_list_zip_command = self._base_zip_command(
        host_out, dist_dir, 'general-tests_list.zip'
    )
    tests_list_zip_command.append('-C')
    tests_list_zip_command.append(str(host_out))
    tests_list_zip_command.append('-f')
    tests_list_zip_command.append(str(os.path.join(host_out, 'general-tests_list')))
    zip_commands.append(tests_list_zip_command)

    return zip_commands

  def _get_soong_vars(self, src_top: pathlib.Path, soong_vars: list[str]) -> dict[str, str]:
    process_result = subprocess.run(
        args=[os.path.join(src_top, 'build/soong/soong_ui.bash'), '--dumpvar-mode', '--abs', soong_vars],
        env=os.environ,
        check=False,
        capture_output=True,
    )
    if not process_result.returncode == 0:
      logging.error('soong dumpvars command failed! stderr:')
      logging.error(process_result.stderr)
      raise RuntimeError('Soong dumpvars failed! See log for stderr.')

    if not process_result.stdout:
      raise RuntimeError('Necessary soong variables ' + soong_vars + ' not found.')

    output = dict()
    for line in process_result.stdout.split('\n'):
      split_line = line.split('=')
      output[split_line[0]]=split_line[1].strip('\'')

    return output

  def get_enabled_flag(self):
    return 'general_tests_optimized'

  @classmethod
  def get_optimized_targets(cls) -> dict[str, OptimizedBuildTarget]:
    return {'general-tests': functools.partial(cls)}


OPTIMIZED_BUILD_TARGETS = {}
OPTIMIZED_BUILD_TARGETS.update(GeneralTestsOptimizer.get_optimized_targets())
