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

import re
import unittest
import optimized_targets


class ExcludeUnusedTargetOptimizerTest(unittest.TestCase):

  def test_target_output_used_target_built(self):
    optimizer = self._get_target_optimizer(self._get_build_context())

    expected_targets = {'test_target'}

    self.assertEqual(optimizer.get_build_targets(), expected_targets)

  def test_target_regex_used_target_built(self):
    build_context = self._get_build_context()
    build_context['testContext']['testInfos'][0]['extraOptions'][0][
        'values'
    ] = ['.*output.zip.*']
    optimizer = self._get_target_optimizer(build_context)

    expected_targets = {'test_target'}

    self.assertEqual(optimizer.get_build_targets(), expected_targets)

  def test_target_output_not_used_target_not_built(self):
    build_context = self._get_build_context()
    build_context['testContext']['testInfos'][0]['extraOptions'] = []
    optimizer = self._get_target_optimizer(build_context)

    expected_targets = set()

    self.assertEqual(optimizer.get_build_targets(), expected_targets)

  def _get_target_optimizer(self, build_context):
    return optimized_targets.ExcludeUnusedTargetOptimizer(
        'test_target',
        build_context,
        [],
        optimized_targets.NullOptimizer('test_target'),
        self._get_target_to_outputs(),
    )

  def _get_build_context(self):
    return {
        'enabledBuildFeatures': [
            'optimized_build',
            'test_target-atp-exclusion',
        ],
        'testContext': {
            'testInfos': [
                {
                    'name': 'atp_test',
                    'target': 'test_target',
                    'branch': 'branch',
                    'extraOptions': [{
                        'key': 'additional-files-filter',
                        'values': ['test_target_output.zip'],
                    }],
                    'command': '/tf/command',
                    'extraBuildTargets': [
                        'extra_build_target',
                    ],
                },
            ],
        },
    }

  def _get_target_to_outputs(self):
    return {'test_target': ['test_target_output.zip']}


if __name__ == '__main__':
  unittest.main()
