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

package android.aconfig.storage.test;

import java.io.File;

public final class TestDataUtils {
    private static final String TEST_PACKAGE_MAP_PATH = "package.map";
    private static final String TEST_FLAG_MAP_PATH = "flag.map";
    private static final String TEST_FLAG_VAL_PATH = "flag.val";
    private static final String TEST_FLAG_INFO_PATH = "flag.info";

    private static final String TESTDATA_PATH =
            "/data/local/tmp/aconfig_storage_file_test_java/testdata";

    public static File getTestPackageMapFile() {
        return new File(TESTDATA_PATH, TEST_PACKAGE_MAP_PATH);
    }

    public static File getTestFlagMapFile() {
        return new File(TESTDATA_PATH, TEST_FLAG_MAP_PATH);
    }

    public static File getTestFlagValFile() {
        return new File(TESTDATA_PATH, TEST_FLAG_VAL_PATH);
    }

    public static File getTestFlagInfoFile() {
        return new File(TESTDATA_PATH, TEST_FLAG_INFO_PATH);
    }
}
