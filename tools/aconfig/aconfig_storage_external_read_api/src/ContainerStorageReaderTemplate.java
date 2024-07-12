// Copyright (C) 2024 The Android Open Source Project
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package android.aconfig.storage;

import java.io.IOException;

/**
 * Reads flags from CONTAINER, searching for package/flag offsets dynamically.
 *
 * @hide
 */
class CONTAINERStorageReader {
  /**
   * Returns {@code true} if the flag is enabled, {@code false} if disabled, in CONTAINER.
   *
   * <p>Calling this without first checking if the flag is present, with {@code hasFlag}, is an
   * error.
   *
   * @param packageName the name of the package containing the flag
   * @param flagName the name of the flag
   * @throws IOException if there is a problem accessing the underlying storage files
   * @throws IllegalStateException if the flag is not in the container
   * @return a boolean indicating whether or not the flag is enabled
   */
  public static boolean CONTAINER_hasFlag(String packageName, String flagName) throws IOException {
    return ExternalStorageReader.hasFlag("CONTAINER", packageName, flagName);
  }

  /**
   * Returns {@code true} if the flag is present, {@code false} if not, in CONTAINER.
   *
   * @param packageName the name of the package containing the flag
   * @param flagName the name of the flag
   * @throws IOException if there is a problem accessing the underlying storage files
   * @throws IllegalStateException if the flag is not in the container
   * @return a boolean indicating whether or not the flag is present
   */
  public static boolean CONTAINER_readFlag(String packageName, String flagName) throws IOException {
    return ExternalStorageReader.readFlag("CONTAINER", packageName, flagName);
  }
}
