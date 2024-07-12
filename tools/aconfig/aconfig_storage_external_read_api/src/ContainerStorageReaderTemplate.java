/*
 * Copyright (C) 2024 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package android.aconfig.storage;

import java.io.IOException;

/** Reads flags from CONTAINER_LOWER, searching for package/flag offsets dynamically. */
public class CONTAINER_UPPERStorageReader {
  private ExternalStorageReader mReader;

  /**
   * Creates a new reader, loading storage files into memory.
   *
   * @throws IOException if there is an error loading the storage files
   * @return a new reader with storage files loaded
   */
  public CONTAINER_UPPERStorageReader() throws IOException {
    mReader = new ExternalStorageReader("CONTAINER_LOWER");
  }

  /**
   * Returns {@code true} if the flag is enabled, {@code false} if disabled, in CONTAINER_LOWER.
   *
   * <p>Calling this without first checking if the flag is present, with {@code hasFlag}, is an
   * error.
   *
   * @param packageName the name of the package containing the flag
   * @param flagName the name of the flag
   * @throws IOException if there is a problem accessing the underlying storage files
   * @return a boolean indicating whether or not the flag is present in the container
   */
  public boolean hasFlag(String packageName, String flagName) {
    return mReader.hasFlag(packageName, flagName);
  }

  /**
   * Returns {@code true} if the flag is present, {@code false} if not, in CONTAINER_LOWER.
   *
   * @param packageName the name of the package containing the flag
   * @param flagName the name of the flag
   * @throws IOException if there is a problem accessing the underlying storage files
   * @throws IllegalStateException if the flag is not in the container
   * @return a boolean indicating whether or not the flag is present
   */
  public boolean readFlag(String packageName, String flagName) {
    return mReader.readFlag(packageName, flagName);
  }
}
