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

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertThrows;
import static org.junit.Assert.assertTrue;

import android.aconfig.storage.AconfigPackageImpl;
import android.aconfig.storage.AconfigStorageException;
import android.aconfig.storage.StorageFileProvider;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.JUnit4;

@RunWith(JUnit4.class)
public class AconfigPackageImplTest {

    private StorageFileProvider pr;

    @Before
    public void setup() {
        pr = new StorageFileProvider(TestDataUtils.TESTDATA_PATH, TestDataUtils.TESTDATA_PATH);
    }

    @Test
    public void testLoad_onlyPackageName() throws Exception {
        AconfigPackageImpl p = new AconfigPackageImpl();
        p.load("com.android.aconfig.storage.test_1", pr);
        assertNotNull(p);
    }

    @Test
    public void testLoad_groupNameFingerprint() throws Exception {
        AconfigPackageImpl p = new AconfigPackageImpl();
        p.load("mockup", "com.android.aconfig.storage.test_1", pr);
        assertNotNull(p);
    }

    @Test
    public void testLoad_error() throws Exception {
        AconfigPackageImpl p = new AconfigPackageImpl();
        // cannot find package
        assertEquals(
                AconfigPackageImpl.ERROR_PACKAGE_NOT_FOUND,
                p.load("mockup", "com.android.aconfig.storage.test_10", pr));
        // cannot find package
        assertEquals(
                AconfigPackageImpl.ERROR_PACKAGE_NOT_FOUND,
                p.load("com.android.aconfig.storage.test_10", pr));
        // cannot find container
        assertEquals(
                AconfigPackageImpl.ERROR_CONTAINER_NOT_FOUND,
                p.load(null, "com.android.aconfig.storage.test_1", pr));
        assertEquals(
                AconfigPackageImpl.ERROR_CONTAINER_NOT_FOUND,
                p.load("test", "com.android.aconfig.storage.test_1", pr));

        // new storage doesn't exist
        pr = new StorageFileProvider("fake/path/", "fake/path/");
        assertEquals(
                AconfigPackageImpl.ERROR_NEW_STORAGE_SYSTEM_NOT_FOUND, p.load("fake_package", pr));

        // file read issue
        pr = new StorageFileProvider(TestDataUtils.TESTDATA_PATH, "fake/path/");
        assertThrows(
                AconfigStorageException.class,
                () -> p.load("mockup", "com.android.aconfig.storage.test_1", pr));
    }

    @Test
    public void testGetBooleanFlagValue_flagName() throws Exception {
        AconfigPackageImpl p = new AconfigPackageImpl();
        p.load("mockup", "com.android.aconfig.storage.test_1", pr);
        assertFalse(p.getBooleanFlagValue("disabled_rw", true));
        assertTrue(p.getBooleanFlagValue("enabled_ro", false));
        assertTrue(p.getBooleanFlagValue("enabled_rw", false));
        assertFalse(p.getBooleanFlagValue("fake", false));
    }

    @Test
    public void testGetBooleanFlagValue_index() throws Exception {
        AconfigPackageImpl p = new AconfigPackageImpl();
        p.load("mockup", "com.android.aconfig.storage.test_1", pr);
        assertFalse(p.getBooleanFlagValue(0));
        assertTrue(p.getBooleanFlagValue(1));
        assertTrue(p.getBooleanFlagValue(2));
    }

    @Test
    public void testHasPackageFingerprint() throws Exception {
        AconfigPackageImpl p = new AconfigPackageImpl();
        p.load("mockup", "com.android.aconfig.storage.test_1", pr);
        assertFalse(p.hasPackageFingerprint());
    }
}
