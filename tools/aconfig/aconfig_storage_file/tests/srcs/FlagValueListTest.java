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

import android.aconfig.storage.FileType;
import android.aconfig.storage.FlagValueList;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.JUnit4;

import java.io.FileInputStream;
import java.io.InputStream;
import java.nio.ByteBuffer;

@RunWith(JUnit4.class)
public class FlagValueListTest {

    @Test
    public void testFlagValueList_rightHeader() throws Exception {
        InputStream input = new FileInputStream(TestDataUtils.getTestFlagValFile());
        ByteBuffer buffer = ByteBuffer.wrap(input.readAllBytes());
        FlagValueList flagValueList = FlagValueList.fromBytes(buffer);
        FlagValueList.Header header = flagValueList.getHeader();
        assertEquals(1, header.getVersion());
        assertEquals("mockup", header.getContainer());
        assertEquals(FileType.FLAG_VAL, header.getFileType());
        assertEquals(35, header.getFileSize());
        assertEquals(8, header.getNumFlags());
        assertEquals(27, header.getBooleanValueOffset());
    }

    @Test
    public void testFlagValueList_rightNode() throws Exception {
        InputStream input = new FileInputStream(TestDataUtils.getTestFlagValFile());
        ByteBuffer buffer = ByteBuffer.wrap(input.readAllBytes());
        FlagValueList flagValueList = FlagValueList.fromBytes(buffer);

        boolean[] expected = new boolean[] {false, true, true, false, true, true, true, true};
        assertEquals(expected.length, flagValueList.size());

        for (int i = 0; i < flagValueList.size(); i++) {
            assertEquals(expected[i], flagValueList.get(i));
        }
    }
}
