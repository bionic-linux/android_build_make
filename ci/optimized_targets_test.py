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

"""Tests for optimized_targets.py"""

import json
import logging
import os
import pathlib
import re
import unittest
from unittest import mock
import optimized_targets
import subprocess
from build_context import BuildContext
from pyfakefs import fake_filesystem_unittest


class GeneralTestsOptimizerTest(fake_filesystem_unittest.TestCase):

  def setUp(self):
    self.setUpPyfakefs()

    os_environ_patcher = mock.patch.dict('os.environ', {})
    self.addCleanup(os_environ_patcher.stop)
    self.mock_os_environ = os_environ_patcher.start()

    self._setup_working_build_env()
    self._write_change_info_file()
    test_mapping_dir = pathlib.Path('/project/path/file/path')
    test_mapping_dir.mkdir(parents=True)
    self._write_test_mapping_file()

  def _setup_working_build_env(self):
    self.change_info_file = pathlib.Path('/tmp/change_info')
    self._write_soong_ui_file()
    pathlib.Path('/tmp/top/host_out_testcases').mkdir(parents=True)
    pathlib.Path('/tmp/top/target_out_testcases').mkdir(parents=True)
    pathlib.Path('/tmp/top/product_out').mkdir(parents=True)
    pathlib.Path('/tmp/top/soong_host_out').mkdir(parents=True)
    pathlib.Path('/tmp/top/host_out').mkdir(parents=True)

    pathlib.Path('/tmp/top/out/dist').mkdir(parents=True)

    self.mock_os_environ.update({
        'CHANGE_INFO': str(self.change_info_file),
        'TOP': '/tmp/top',
        'DIST_DIR': '/tmp/top/out/dist',
    })

  def _write_soong_ui_file(self):
    soong_path = pathlib.Path('/tmp/top/build/soong')
    soong_path.mkdir(parents=True)
    with open(os.path.join(soong_path, 'soong_ui.bash'), 'w') as f:
      f.write("""
              #/bin/bash
              echo HOST_OUT_TESTCASES='/tmp/top/host_out_testcases'
              echo TARGET_OUT_TESTCASES='/tmp/top/target_out_testcases'
              echo PRODUCT_OUT='/tmp/top/product_out'
              echo SOONG_HOST_OUT='/tmp/top/soong_host_out'
              echo HOST_OUT='/tmp/top/host_out'
              """)
    os.chmod(os.path.join(soong_path, 'soong_ui.bash'), 0o666)

  def _write_change_info_file(self):
    change_info_contents = {
        'changes': [{
            'projectPath': '/project/path',
            'revisions': [{
                'fileInfos': [{
                    'path': 'file/path/file_name',
                }],
            }],
        }]
    }

    with open(self.change_info_file, 'w') as f:
      json.dump(change_info_contents, f)

  def _write_test_mapping_file(self):
    test_mapping_contents = {
        'test-mapping-group': [
            {
                'name': 'test_mapping_module',
            },
        ],
    }

    with open('/project/path/file/path/TEST_MAPPING', 'w') as f:
      json.dump(test_mapping_contents, f)

  def test_general_tests_optimized(self):
    optimizer = self._create_general_tests_optimizer()

    build_targets = optimizer.get_build_targets()

    expected_build_targets = set(
        optimized_targets.GeneralTestsOptimizer._REQUIRED_MODULES
    )
    expected_build_targets.add('test_mapping_module')

    self.assertSetEqual(build_targets, expected_build_targets)

  def test_no_change_info_no_optimization(self):
    del os.environ['CHANGE_INFO']

    optimizer = self._create_general_tests_optimizer()

    build_targets = optimizer.get_build_targets()

    self.assertSetEqual(build_targets, {'general-tests'})

  def test_mapping_groups_unused_module_not_built(self):
    test_context = self._create_test_context()
    test_context['testInfos'][0]['extraOptions'] = [
        {
            'key': 'additional-files-filter',
            'values': ['general-tests.zip'],
        },
        {
            'key': 'test-mapping-test-group',
            'values': ['unused-test-mapping-group'],
        },
    ]
    optimizer = self._create_general_tests_optimizer(
        build_context=self._create_build_context(test_context=test_context)
    )

    build_targets = optimizer.get_build_targets()

    expected_build_targets = set(
        optimized_targets.GeneralTestsOptimizer._REQUIRED_MODULES
    )
    self.assertSetEqual(build_targets, expected_build_targets)

  def test_general_tests_used_by_non_test_mapping_test_no_optimization(self):
    test_context = self._create_test_context()
    test_context['testInfos'][0]['extraOptions'] = [{
        'key': 'additional-files-filter',
        'values': ['general-tests.zip'],
    }]
    optimizer = self._create_general_tests_optimizer(
        build_context=self._create_build_context(test_context=test_context)
    )

    build_targets = optimizer.get_build_targets()

    self.assertSetEqual(build_targets, {'general-tests'})

  def test_malformed_change_info_raises(self):
    with open(self.change_info_file, 'w') as f:
      f.write('not change info')

    optimizer = self._create_general_tests_optimizer()

    with self.assertRaises(json.decoder.JSONDecodeError):
      build_targets = optimizer.get_build_targets()

  def test_malformed_test_mapping_raises(self):
    with open('/project/path/file/path/TEST_MAPPING', 'w') as f:
      f.write('not test mapping')

    optimizer = self._create_general_tests_optimizer()

    with self.assertRaises(json.decoder.JSONDecodeError):
      build_targets = optimizer.get_build_targets()

  @mock.patch('subprocess.run')
  def test_packaging_outputs(self, subprocess_run):
    return_value = subprocess.CompletedProcess(args=[], returncode=0)
    return_value.stdout = """HOST_OUT_TESTCASES='/tmp/top/host_out_testcases'
TARGET_OUT_TESTCASES='/tmp/top/target_out_testcases'
PRODUCT_OUT='/tmp/top/product_out'
SOONG_HOST_OUT='/tmp/top/soong_host_out'
HOST_OUT='/tmp/top/host_out'"""
    subprocess_run.return_value = return_value
    optimizer = self._create_general_tests_optimizer()

    optimizer.get_build_targets()
    package_commands = optimizer.get_package_outputs_commands()

    #self.assertListEqual(package_commands, [])

  def _create_general_tests_optimizer(
      self, build_context: BuildContext = None
  ):
    if not build_context:
      build_context = self._create_build_context()
    return optimized_targets.GeneralTestsOptimizer(
        'general-tests', build_context, None
    )

  def _create_build_context(
      self,
      general_tests_optimized: bool = True,
      test_context: dict[str, any] = None,
  ) -> BuildContext:
    if not test_context:
      test_context = self._create_test_context()
    build_context_dict = {}
    build_context_dict['enabledBuildFeatures'] = [{'name': 'optimized_build'}]
    if general_tests_optimized:
      build_context_dict['enabledBuildFeatures'].append({'name': 'general_tests_optimized'})
    build_context_dict['testContext'] = test_context
    return BuildContext(build_context_dict)

  def _create_test_context(self):
    return {
        'testInfos': [
            {
                'name': 'atp_test',
                'target': 'test_target',
                'branch': 'branch',
                'extraOptions': [
                    {
                        'key': 'additional-files-filter',
                        'values': ['general-tests.zip'],
                    },
                    {
                        'key': 'test-mapping-test-group',
                        'values': ['test-mapping-group'],
                    },
                ],
                'command': '/tf/command',
                'extraBuildTargets': [
                    'extra_build_target',
                ],
            },
        ],
    }


if __name__ == '__main__':
  # Setup logging to be silent so unit tests can pass through TF.
  logging.disable(logging.ERROR)
  unittest.main()
