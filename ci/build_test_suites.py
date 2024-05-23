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

"""Build script for the CI `test_suites` target."""

import argparse
import json
import logging
import os
import pathlib
import subprocess
import sys
from typing import Callable
import optimized_targets


REQUIRED_ENV_VARS = frozenset(['TARGET_PRODUCT', 'TARGET_RELEASE', 'TOP'])
SOONG_UI_EXE_REL_PATH = 'build/soong/soong_ui.bash'


class Error(Exception):

  def __init__(self, message):
    super().__init__(message)


class BuildFailureError(Error):

  def __init__(self, return_code):
    super().__init__(f'Build command failed with return code: f{return_code}')
    self.return_code = return_code


class BuildPlanner:

  def __init__(
      self,
      build_context: dict[str, any],
      args: argparse.Namespace,
      target_optimizations: dict[str, optimized_targets.OptimizedBuildTarget],
  ):
    self.build_context = build_context
    self.args = args
    self.target_optimizations = target_optimizations

  def create_build_plan(self):

    if 'optimized_build' not in self.build_context['enabled_build_features']:
      return BuildPlan(set(self.args.extra_targets), set())

    build_targets = set()
    packaging_functions = set()
    for target in self.args.extra_targets:
      if target not in self.target_optimizations:
        build_targets.add(target)
        continue

      target_optimizer = self.target_optimizations[target](
          target, self.build_context, self.args
      )
      build_targets.update(target_optimizer.get_build_targets())
      packaging_functions.add(target_optimizer.package_outputs)

    return BuildPlan(build_targets, packaging_functions)


class BuildPlan:

  def __init__(
      self,
      build_targets: set[str],
      packaging_functions: set[Callable[..., None]],
  ):
    self.build_targets = build_targets
    self.packaging_functions = packaging_functions


def build_test_suites(argv: list[str]) -> int:
  """Builds all test suites passed in, optimizing based on the build_context content.

  Args:
    argv: The command line arguments passed in.

  Returns:
    The exit code of the build.
  """
  args = parse_args(argv)
  check_required_env()
  build_context = load_build_context()
  build_planner = BuildPlanner(
      build_context, args, optimized_targets.OPTIMIZED_BUILD_TARGETS
  )
  build_plan = build_planner.create_build_plan()

  try:
    execute_build_plan(build_plan, args)
  except BuildFailureError as e:
    logging.error('Build command failed! Check build_log for details.')
    return e.return_code

  return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
  argparser = argparse.ArgumentParser()

  argparser.add_argument(
      'extra_targets', nargs='*', help='Extra test suites to build.'
  )

  return argparser.parse_args(argv)


def check_required_env():
  """Check for required env vars.

  Raises:
    RuntimeError: If any required env vars are not found.
  """
  missing_env_vars = sorted(v for v in REQUIRED_ENV_VARS if v not in os.environ)

  if not missing_env_vars:
    return

  t = ','.join(missing_env_vars)
  raise Error(f'Missing required environment variables: {t}')


def load_build_context():
  build_context_path = pathlib.Path(os.environ.get('BUILD_CONTEXT', ''))
  if build_context_path.is_file():
    try:
      with open(build_context_path, 'r') as f:
        return json.load(f)
    except json.decoder.JSONDecodeError as e:
      raise Error(f'Failed to load JSON file: {build_context_path}')

  return empty_build_context()


def empty_build_context():
  return {'enabled_build_features': []}


def execute_build_plan(build_plan: BuildPlan, args: argparse.Namespace):
  build_command = []
  build_command.append(get_top().joinpath(SOONG_UI_EXE_REL_PATH))
  build_command.append('--make-mode')
  build_command.extend(build_plan.build_targets)

  try:
    run_command(args)
  except subprocess.CalledProcessError as e:
    raise BuildFailureError(e.returncode) from e

  for packaging_function in build_plan.packaging_functions:
    packaging_function()


def get_top() -> pathlib.Path:
  return pathlib.Path(os.environ['TOP'])


def run_command(args: list[str], stdout=None):
  subprocess.run(args=args, check=True, stdout=stdout)


def main(argv):
  sys.exit(build_test_suites(argv))
