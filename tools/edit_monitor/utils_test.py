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

"""Unittests for DaemonManager."""


import os
import unittest
from edit_monitor import utils

TEST_USER = 'test_user'
TEST_FEATURE = 'test_feature'
ENABLE_TEST_FEATURE_FLAG = 'ENABLE_TEST_FEATURE'
ROLLOUT_TEST_FEATURE_FLAG = 'ROLLOUT_TEST_FEATURE'


class EnableFeatureTest(unittest.TestCase):

  def test_feature_enabled_without_flag(self):
    self.assertTrue(utils.is_feature_enabled(TEST_FEATURE, TEST_USER))

  def test_feature_disabled_with_flag(self):
    os.environ[ENABLE_TEST_FEATURE_FLAG] = 'false'
    self.assertFalse(
        utils.is_feature_enabled(
            TEST_FEATURE, TEST_USER, ENABLE_TEST_FEATURE_FLAG
        )
    )

  def test_feature_enabled_with_flag(self):
    os.environ[ENABLE_TEST_FEATURE_FLAG] = 'true'
    self.assertTrue(
        utils.is_feature_enabled(
            TEST_FEATURE, TEST_USER, ENABLE_TEST_FEATURE_FLAG
        )
    )

  def test_feature_disabled_with_invalid_rollout_percentage(self):
    os.environ[ROLLOUT_TEST_FEATURE_FLAG] = 'invalid value'
    self.assertFalse(
        utils.is_feature_enabled(
            TEST_FEATURE,
            TEST_USER,
            ENABLE_TEST_FEATURE_FLAG,
            ROLLOUT_TEST_FEATURE_FLAG,
        )
    )

  def test_feature_disabled_with_out_range_rollout_percentage(self):
    os.environ[ROLLOUT_TEST_FEATURE_FLAG] = '-1'
    self.assertFalse(
        utils.is_feature_enabled(
            TEST_FEATURE,
            TEST_USER,
            ENABLE_TEST_FEATURE_FLAG,
            ROLLOUT_TEST_FEATURE_FLAG,
        )
    )

    os.environ[ROLLOUT_TEST_FEATURE_FLAG] = '101'
    self.assertFalse(
        utils.is_feature_enabled(
            TEST_FEATURE,
            TEST_USER,
            ENABLE_TEST_FEATURE_FLAG,
            ROLLOUT_TEST_FEATURE_FLAG,
        )
    )

  def test_feature_enabled_with_rollout_percentage(self):
    os.environ[ROLLOUT_TEST_FEATURE_FLAG] = '90'
    self.assertTrue(
        utils.is_feature_enabled(
            TEST_FEATURE,
            TEST_USER,
            ENABLE_TEST_FEATURE_FLAG,
            ROLLOUT_TEST_FEATURE_FLAG,
        )
    )

  def test_feature_disabled_with_rollout_percentage(self):
    os.environ[ROLLOUT_TEST_FEATURE_FLAG] = '10'
    self.assertFalse(
        utils.is_feature_enabled(
            TEST_FEATURE,
            TEST_USER,
            ENABLE_TEST_FEATURE_FLAG,
            ROLLOUT_TEST_FEATURE_FLAG,
        )
    )


if __name__ == '__main__':
  unittest.main()
