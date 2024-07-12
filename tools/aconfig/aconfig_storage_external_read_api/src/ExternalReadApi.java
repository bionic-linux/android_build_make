package android.aconfig.storage;

import java.io.FileInputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.MappedByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.channels.FileChannel.MapMode;

public class ExternalReadApi {
  private static final String MAP_PATH = "/metadata/aconfig/maps/";
  private static final String BOOT_PATH = "/metadata/aconfig/boot/";

  public static boolean readFlag(String container, String packageName, String flagName) {
    PackageTable.Node packageNode = readPackageNode(container, packageName);
    if (packageNode == null) {
      throw new IllegalStateException("");
    }

    Integer mFlagOffset = readFlagOffset(container, packageNode.getPackageId(), flagName);
    if (mFlagOffset == null) {
      throw new IllegalStateException("");
    }

    Boolean flagValue = readFlagValue(container, packageNode.getBooleanStartIndex() + mFlagOffset);
    if (flagValue == null) {
      throw new IllegalStateException("");
    }

    return flagValue;
  }

  public static boolean hasFlag(String container, String packageName, String flagName) {
    PackageTable.Node packageNode = readPackageNode(container, packageName);
    if (packageNode == null) {
      return false;
    }

    Integer mFlagOffset = readFlagOffset(container, packageNode.getPackageId(), flagName);
    if (mFlagOffset == null) {
      return false;
    }

    Boolean flagValue = readFlagValue(container, packageNode.getBooleanStartIndex() + mFlagOffset);
    if (flagValue == null) {
      return false;
    }

    return true;
  }

  private static PackageTable.Node readPackageNode(String container, String packageName) {
    String packageMapFile = MAP_PATH + container + ".package.map";
    PackageTable mPackageTable = PackageTable.fromBytes(mapStorageFile(packageMapFile));
    return mPackageTable.get(packageName);
  }

  private static Integer readFlagOffset(String container, int packageId, String flagName) {
    String flagMapFile = MAP_PATH + container + ".flag.map";
    FlagTable mFlagTable = FlagTable.fromBytes(mapStorageFile(flagMapFile));
    FlagTable.Node flagNode = mFlagTable.get(packageId, flagName);
    if (flagNode == null) {
      return null;
    }
    return flagNode.getFlagIndex();
  }

  private static Boolean readFlagValue(String container, int index) {
    String flagValueFile = BOOT_PATH + container + ".val";
    FlagValueList mFlagValueList = FlagValueList.fromBytes(mapStorageFile(flagValueFile));
    return mFlagValueList.get(index);
  }

  public static MappedByteBuffer mapStorageFile(String file) {
    try {
    FileInputStream stream = new FileInputStream(file);
    FileChannel channel = stream.getChannel();
    return channel.map(FileChannel.MapMode.READ_ONLY, 0, channel.size());
    } catch (IOException e) {
        return null;
    }
  }
}
