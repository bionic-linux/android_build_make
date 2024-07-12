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

import java.io.FileInputStream;
import java.io.IOException;
import java.nio.MappedByteBuffer;
import java.nio.channels.FileChannel;

/**
 * Reads flags from a container, searching for package/flag offsets dynamically.
 *
 * @hide
 */
public class ExternalStorageReader {
  private static final String MAP_PATH = "/metadata/aconfig/maps/";
  private static final String BOOT_PATH = "/metadata/aconfig/boot/";

  private PackageTable mPackageTable;
  private FlagTable mFlagTable;
  private FlagValueList mFlagValueList;

  public ExternalStorageReader(String container) throws IOException {
    String packageMapFile = MAP_PATH + container + ".package.map";
    String flagMapFile = MAP_PATH + container + ".flag.map";
    String flagValueFile = BOOT_PATH + container + ".val";

    mPackageTable = PackageTable.fromBytes(mapStorageFile(packageMapFile));
    mFlagTable = FlagTable.fromBytes(mapStorageFile(flagMapFile));
    mFlagValueList = FlagValueList.fromBytes(mapStorageFile(flagValueFile));
  }

  /**
   * Returns {@code true} if the flag is enabled, {@code false} if disabled.
   *
   * <p>Calling this without first checking if the flag is present, with {@code hasFlag}, is an
   * error.
   *
   * @param container the container in which to search for the flag
   * @param packageName the name of the package containing the flag
   * @param flagName the name of the flag
   * @throws IOException if there is a problem accessing the underlying storage files
   * @throws IllegalStateException if the flag is not in the container
   * @return a boolean indicating whether or not the flag is enabled
   */
  public boolean readFlag(String packageName, String flagName) {
    PackageTable.Node mPackageNode = mPackageTable.get(packageName);
    if (mPackageNode == null) {
      throw new IllegalStateException(
          "could not find package node for '" + packageName + "' in 'CONTAINER'");
    }

    FlagTable.Node mFlagNode = mFlagTable.get(mPackageNode.getPackageId(), flagName);
    if (mFlagNode == null) {
      throw new IllegalStateException(
          "could not find flag node for '" + flagName + "' in 'CONTAINER'");
    }

    Boolean mValue =
        mFlagValueList.get(mPackageNode.getBooleanStartIndex() + mFlagNode.getFlagIndex());
    if (mValue == null) {
      throw new IllegalStateException(
          "could not find flag value for '" + flagName + "' in 'CONTAINER'");
    }

    return mValue;
  }

  /**
   * Returns {@code true} if {@code container} contains {@code packageName.flagName}.
   *
   * @param container the container in which to search for the flag
   * @param packageName the name of the package containing the flag
   * @param flagName the name of the flag
   * @throws IOException if there is a problem accessing the underlying storage files
   * @return a boolean indicating whether or not the container contains the flag
   */
  public boolean hasFlag(String packageName, String flagName) {
    PackageTable.Node mPackageNode = mPackageTable.get(packageName);
    if (mPackageNode == null) {
      return false;
    }

    FlagTable.Node mFlagNode = mFlagTable.get(mPackageNode.getPackageId(), flagName);
    if (mFlagNode == null) {
      return false;
    }

    Boolean mValue =
        mFlagValueList.get(mPackageNode.getBooleanStartIndex() + mFlagNode.getFlagIndex());
    if (mValue == null) {
      return false;
    }

    return true;
  }

  private MappedByteBuffer mapStorageFile(String file) throws IOException {
    FileInputStream stream = new FileInputStream(file);
    FileChannel channel = stream.getChannel();
    return channel.map(FileChannel.MapMode.READ_ONLY, 0, channel.size());
  }
}
