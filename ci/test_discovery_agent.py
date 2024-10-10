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
class TestDiscoveryAgent:
  """Test discovery agent."""

  _AOSP_TRADEFED_JAR_RELEVANT_FILES_PATH = "../../../tools/tradefederation/prebuilts/filegroups/tradefed/"

  def __init__(
      self,
      tradefed_args: list[str],
      test_mapping_zip_path: str,
      tradefed_jar_revelant_files_path: str = _AOSP_TRADEFED_JAR_RELEVANT_FILES_PATH,
  ):
    self.tradefed_args = tradefed_args
    self.test_mapping_zip_path = test_mapping_zip_path
    self.tradefed_jar_relevant_files_path = tradefed_jar_revelant_files_path

  def discover_test_zip_regexes(self) -> list[str]:
    """Discover test zip regexes."""
    return []

  def discover_test_modules(self) -> list[str]:
    """Discover test modules."""
    return []
