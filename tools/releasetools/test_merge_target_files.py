#
# Copyright (C) 2017 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import base64
import os.path
import zipfile

import common
import test_utils
from merge_target_files import (
    read_config_list, validate_config_lists)

class MergeTargetFilesTest(test_utils.ReleaseToolsTestCase):
  def setUp(self):
    self.testdata_dir = test_utils.get_testdata_dir()

  def test_read_config_list(self):
    system_item_list_file = os.path.join(
        self.testdata_dir,
        'merge_config_system_item_list')
    system_item_list = read_config_list(system_item_list_file)
    expected_system_item_list = [
        'META/apkcerts.txt',
        'META/filesystem_config.txt',
        'META/root_filesystem_config.txt',
        'META/system_manifest.xml',
        'META/system_matrix.xml',
        'META/update_engine_config.txt',
        'PRODUCT/*',
        'ROOT/*',
        'SYSTEM/*',
    ]
    self.assertItemsEqual(system_item_list, expected_system_item_list)

  def test_validate_config_lists(self):
    # TODO
    self.assertTrue(True)
