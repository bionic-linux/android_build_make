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

"""Script to build only the necessary modules for general-tests along

with whatever other targets are passed in.
"""

import argparse
from collections.abc import Sequence
import json
import logging
import os
import pathlib
import re
import signal
import subprocess
import sys
from typing import Any

import test_mapping_module_retriever


class BuildFailure(Exception):
  pass


# List of modules that are always required to be in general-tests.zip
REQUIRED_MODULES = frozenset(
    ['cts-tradefed', 'vts-tradefed', 'compatibility-host-util']
)

REQUIRED_ENV_VARS = frozenset(['TARGET_PRODUCT', 'TARGET_RELEASE'])

SOONG_ZIP_EXE_REL_PATH = 'prebuilts/build-tools/linux-x86/bin/soong_zip'
SOONG_UI_EXE_REL_PATH = 'build/soong/soong_ui.bash'


def get_top() -> pathlib.Path:
  return pathlib.Path(os.environ.get('TOP', os.getcwd()))


def build_test_suites(argv):
  check_required_env()
  args = parse_args(argv)

  try:
    if is_optimization_enabled():
      # Call the class to map changed files to modules to build.
      # TODO(lucafarsi): Move this into a replaceable class.
      build_affected_modules(args)
    else:
      build_everything(args)
  except BuildFailure:
    logging.error('Build command failed! Check build_log for details.')
    return 1

  return 0


def check_required_env():
  for env_var in REQUIRED_ENV_VARS:
    if env_var not in os.environ:
      raise RuntimeError(f'Required env var {env_var} not found! Aborting.')


def parse_args(argv):
  argparser = argparse.ArgumentParser()
  argparser.add_argument(
      'extra_targets', nargs='*', help='Extra test suites to build.'
  )
  argparser.add_argument('--change_info', nargs='?')

  return argparser.parse_args()


def is_optimization_enabled() -> bool:
  # TODO(lucafarsi): switch back to building only affected general-tests modules
  # in presubmit once ready.
  # if os.environ.get('BUILD_NUMBER')[0] == 'P':
  #   return True
  return False


def build_everything(args: argparse.Namespace):
  build_command = base_build_command(args, args.extra_targets)
  build_command.append('general-tests')

  try:
    run_command(build_command)
  except subprocess.CalledProcessError:
    raise BuildFailure


def build_affected_modules(args: argparse.Namespace):
  modules_to_build = find_modules_to_build(
      pathlib.Path(args.change_info), args.extra_targets
  )

  # Call the build command with everything.
  build_command = base_build_command(args, args.extra_targets)
  build_command.extend(modules_to_build)
  # When not building general-tests we also have to build the general tests
  # shared libs.
  build_command.append('general-tests-shared-libs')

  try:
    run_command(build_command)
  except subprocess.CalledProcessError:
    raise BuildFailure

  zip_build_outputs(modules_to_build)


def base_build_command(
    args: argparse.Namespace, extra_targets: set[str]
) -> list:
  build_command = []
  build_command.append('time')
  build_command.append(os.path.join(get_top(), SOONG_UI_EXE_REL_PATH))
  build_command.append('--make-mode')
  build_command.append('dist')
  build_command.extend(extra_targets)

  return build_command


def run_command(args: list[str], print_cmd: bool = True):
  if print_cmd:
    print('+ ' + str(args))
  proc = subprocess.run(args=args, check=True)


def find_modules_to_build(
    change_info: pathlib.Path, extra_required_modules: list[str]
) -> set[str]:
  changed_files = find_changed_files(change_info)

  test_mappings = test_mapping_module_retriever.GetTestMappings(
      changed_files, set()
  )

  modules_to_build = set(REQUIRED_MODULES)
  if extra_required_modules:
    modules_to_build.update(extra_required_modules)

  modules_to_build.update(find_affected_modules(test_mappings, changed_files))

  return modules_to_build


def find_changed_files(change_info: pathlib.Path) -> set[str]:
  with open(change_info) as change_info_file:
    change_info_contents = json.load(change_info_file)

  changed_files = set()

  for change in change_info_contents['changes']:
    project_path = change.get('projectPath') + '/'

    for revision in change.get('revisions'):
      for file_info in revision.get('fileInfos'):
        changed_files.add(project_path + file_info.get('path'))

  return changed_files


def find_affected_modules(
    test_mappings: dict[str, Any], changed_files: set[str]
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
    for group in test_mapping.values():
      for entry in group:
        module_name = entry.get('name', None)

        if not module_name:
          continue

        file_patterns = entry.get('file_patterns')
        if not file_patterns:
          modules.add(module_name)
          continue

        if matches_file_patterns(file_patterns, changed_files):
          modules.add(module_name)
          continue

  return modules


# TODO(lucafarsi): Share this logic with the original logic in
# test_mapping_test_retriever.py
def matches_file_patterns(
    file_patterns: list[set], changed_files: set[str]
) -> bool:
  for changed_file in changed_files:
    for pattern in file_patterns:
      if re.search(pattern, changed_file):
        return True

  return False


def zip_build_outputs(modules_to_build: set[str]):
  src_top = get_top()

  # Call dumpvars to get the necessary things.
  # TODO(lucafarsi): Don't call soong_ui 4 times for this, --dumpvars-mode can
  # do it but it requires parsing.
  host_out_testcases = pathlib.Path(get_soong_var('HOST_OUT_TESTCASES'))
  target_out_testcases = pathlib.Path(get_soong_var('TARGET_OUT_TESTCASES'))
  product_out = pathlib.Path(get_soong_var('PRODUCT_OUT'))
  soong_host_out = pathlib.Path(get_soong_var('SOONG_HOST_OUT'))
  host_out = pathlib.Path(get_soong_var('HOST_OUT'))
  dist_dir = pathlib.Path(get_soong_var('DIST_DIR'))

  # Call the class to package the outputs.
  # TODO(lucafarsi): Move this code into a replaceable class.
  host_paths = []
  target_paths = []
  host_config_files = []
  target_config_files = []
  for module in modules_to_build:
    host_path = os.path.join(host_out_testcases, module)
    if os.path.exists(host_path):
      host_paths.append(host_path)
      collect_config_files(src_top, host_path, host_config_files)

    target_path = os.path.join(target_out_testcases, module)
    if os.path.exists(target_path):
      target_paths.append(target_path)
      collect_config_files(src_top, target_path, target_config_files)

  zip_test_configs_zips(
      dist_dir, host_out, product_out, host_config_files, target_config_files
  )

  zip_command = base_zip_command(dist_dir, 'general-tests.zip')

  # Add host testcases.
  zip_command.extend(
      zip_entry(
          relative_root=os.path.join(src_top, soong_host_out),
          prefix='host',
          directories=host_paths,
      )
  )

  # Add target testcases.
  zip_command.extend(
      zip_entry(
          relative_root=os.path.join(src_top, product_out),
          prefix='target',
          directories=target_paths,
      )
  )

  # TODO(lucafarsi): Push this logic into a general-tests-minimal build command
  # Add necessary tools. These are also hardcoded in general-tests.mk.
  framework_path = os.path.join(soong_host_out, 'framework')

  zip_command.extend(
      zip_entry(
          relative_root=framework_path,
          prefix=os.path.join('host', 'tools'),
          files=[
              os.path.join(framework_path, 'cts-tradefed.jar'),
              os.path.join(framework_path, 'compatibility-host-util.jar'),
              os.path.join(framework_path, 'vts-tradefed.jar'),
          ],
      )
  )

  run_command(zip_command, print_cmd=False)


def zip_entry(
    relative_root: str = None,
    prefix: str = None,
    files: list[str] = [],
    directories: list[str] = [],
    list_files: list[str] = [],
) -> list[str]:
  entry = []
  if relative_root:
    entry.append('-C')
    entry.append(relative_root)

  if prefix:
    entry.append('-P')
    entry.append(prefix)

  for file in files:
    entry.append('-f')
    entry.append(file)

  for directory in directories:
    entry.append('-D')
    entry.append(directory)

  for list_file in list_files:
    entry.append('-l')
    entry.append(list_file)

  return entry


def collect_config_files(
    src_top: pathlib.Path, root_dir: pathlib.Path, config_files: list[str]
):
  for root, dirs, files in os.walk(os.path.join(src_top, root_dir)):
    for file in files:
      if file.endswith('.config'):
        config_files.append(os.path.join(root_dir, file))


def base_zip_command(dist_dir: pathlib.Path, name: str) -> list[str]:
  return [
      'time',
      os.path.join(get_top(), SOONG_ZIP_EXE_REL_PATH),
      '-d',
      '-o',
      os.path.join(dist_dir, name),
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
def zip_test_configs_zips(
    dist_dir: pathlib.Path,
    host_out: pathlib.Path,
    product_out: pathlib.Path,
    host_config_files: list[str],
    target_config_files: list[str],
):
  with open(
      os.path.join(host_out, 'host_general-tests_list'), 'w'
  ) as host_list_file, open(
      os.path.join(product_out, 'target_general-tests_list'), 'w'
  ) as target_list_file, open(
      os.path.join(host_out, 'general-tests_list'), 'w'
  ) as list_file:

    for config_file in host_config_files:
      host_list_file.write(config_file + '\n')
      list_file.write(
          os.path.join('host', os.path.relpath(config_file, host_out)) + '\n'
      )

    for config_file in target_config_files:
      target_list_file.write(config_file + '\n')
      list_file.write(
          os.path.join('target', os.path.relpath(config_file, product_out))
          + '\n'
      )

  tests_config_zip_command = base_zip_command(
      dist_dir, 'general-tests_configs.zip'
  )
  tests_config_zip_command.extend(
      zip_entry(
          relative_root=host_out,
          prefix='host',
          list_files=[os.path.join(host_out, 'host_general-tests_list')],
      )
  )
  tests_config_zip_command.extend(
      zip_entry(
          relative_root=product_out,
          prefix='target',
          list_files=[os.path.join(product_out, 'target_general-tests_list')],
      )
  )
  run_command(tests_config_zip_command, print_cmd=False)

  tests_list_zip_command = base_zip_command(dist_dir, 'general-tests_list.zip')
  tests_list_zip_command.extend(
      zip_entry(
          relative_root=host_out,
          files=[os.path.join(host_out, 'general-tests_list')],
      )
  )
  run_command(tests_list_zip_command, print_cmd=False)


def get_soong_var(var: str) -> str:
  proc = subprocess.run(
      args=[
          os.path.join(get_top(), SOONG_UI_EXE_REL_PATH),
          '--dumpvar-mode',
          '--abs',
          var,
      ],
      text=True,
      capture_output=True,
      check=True,
  )

  value = proc.stdout.rstrip('\n')
  if not value:
    raise RuntimeError('Necessary soong variable ' + var + ' not found.')

  return value


def main(argv):
  sys.exit(build_test_suites(argv))
