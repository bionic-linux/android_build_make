#
# Copyright (C) 2018 The Android Open Source Project
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

"""
Utils for running unittests.
"""

import os
import os.path
import re
import struct
<<<<<<< HEAD   (4be654 Merge "Merge empty history for sparse-7121469-L4290000080720)
=======
import sys
import unittest
import zipfile
>>>>>>> BRANCH (fe6ad7 Merge "Version bump to RBT1.210107.001.A1 [core/build_id.mk])

import common


def get_testdata_dir():
  """Returns the testdata dir, in relative to the script dir."""
  # The script dir is the one we want, which could be different from pwd.
  current_dir = os.path.dirname(os.path.realpath(__file__))
  return os.path.join(current_dir, 'testdata')


def get_search_path():
  """Returns the search path that has 'framework/signapk.jar' under."""
  current_dir = os.path.dirname(os.path.realpath(__file__))
  for path in (
      # In relative to 'build/make/tools/releasetools' in the Android source.
      ['..'] * 4 + ['out', 'host', 'linux-x86'],
      # Or running the script unpacked from otatools.zip.
      ['..']):
    full_path = os.path.realpath(os.path.join(current_dir, *path))
    signapk_path = os.path.realpath(
        os.path.join(full_path, 'framework', 'signapk.jar'))
    if os.path.exists(signapk_path):
      return full_path
  return None


def construct_sparse_image(chunks):
  """Returns a sparse image file constructed from the given chunks.

  From system/core/libsparse/sparse_format.h.
  typedef struct sparse_header {
    __le32 magic;  // 0xed26ff3a
    __le16 major_version;  // (0x1) - reject images with higher major versions
    __le16 minor_version;  // (0x0) - allow images with higer minor versions
    __le16 file_hdr_sz;  // 28 bytes for first revision of the file format
    __le16 chunk_hdr_sz;  // 12 bytes for first revision of the file format
    __le32 blk_sz;  // block size in bytes, must be a multiple of 4 (4096)
    __le32 total_blks;  // total blocks in the non-sparse output image
    __le32 total_chunks;  // total chunks in the sparse input image
    __le32 image_checksum;  // CRC32 checksum of the original data, counting
                            // "don't care" as 0. Standard 802.3 polynomial,
                            // use a Public Domain table implementation
  } sparse_header_t;

  typedef struct chunk_header {
    __le16 chunk_type;  // 0xCAC1 -> raw; 0xCAC2 -> fill;
                        // 0xCAC3 -> don't care
    __le16 reserved1;
    __le32 chunk_sz;  // in blocks in output image
    __le32 total_sz;  // in bytes of chunk input file including chunk header
                      // and data
  } chunk_header_t;

  Args:
    chunks: A list of chunks to be written. Each entry should be a tuple of
        (chunk_type, block_number).

  Returns:
    Filename of the created sparse image.
  """
  SPARSE_HEADER_MAGIC = 0xED26FF3A
  SPARSE_HEADER_FORMAT = "<I4H4I"
  CHUNK_HEADER_FORMAT = "<2H2I"

  sparse_image = common.MakeTempFile(prefix='sparse-', suffix='.img')
  with open(sparse_image, 'wb') as fp:
    fp.write(struct.pack(
        SPARSE_HEADER_FORMAT, SPARSE_HEADER_MAGIC, 1, 0, 28, 12, 4096,
        sum(chunk[1] for chunk in chunks),
        len(chunks), 0))

    for chunk in chunks:
      data_size = 0
      if chunk[0] == 0xCAC1:
        data_size = 4096 * chunk[1]
      elif chunk[0] == 0xCAC2:
        data_size = 4
      elif chunk[0] == 0xCAC3:
        pass
      else:
        assert False, "Unsupported chunk type: {}".format(chunk[0])

      fp.write(struct.pack(
          CHUNK_HEADER_FORMAT, chunk[0], 0, chunk[1], data_size + 12))
      if data_size != 0:
        fp.write(os.urandom(data_size))

  return sparse_image
<<<<<<< HEAD   (4be654 Merge "Merge empty history for sparse-7121469-L4290000080720)
=======


class MockScriptWriter(object):
  """A class that mocks edify_generator.EdifyGenerator.

  It simply pushes the incoming arguments onto script stack, which is to assert
  the calls to EdifyGenerator functions.
  """

  def __init__(self, enable_comments=False):
    self.lines = []
    self.enable_comments = enable_comments

  def Mount(self, *args):
    self.lines.append(('Mount',) + args)

  def AssertDevice(self, *args):
    self.lines.append(('AssertDevice',) + args)

  def AssertOemProperty(self, *args):
    self.lines.append(('AssertOemProperty',) + args)

  def AssertFingerprintOrThumbprint(self, *args):
    self.lines.append(('AssertFingerprintOrThumbprint',) + args)

  def AssertSomeFingerprint(self, *args):
    self.lines.append(('AssertSomeFingerprint',) + args)

  def AssertSomeThumbprint(self, *args):
    self.lines.append(('AssertSomeThumbprint',) + args)

  def Comment(self, comment):
    if not self.enable_comments:
      return
    self.lines.append('# {}'.format(comment))

  def AppendExtra(self, extra):
    self.lines.append(extra)

  def __str__(self):
    return '\n'.join(self.lines)


class ReleaseToolsTestCase(unittest.TestCase):
  """A common base class for all the releasetools unittests."""

  def tearDown(self):
    common.Cleanup()

class PropertyFilesTestCase(ReleaseToolsTestCase):

  @staticmethod
  def construct_zip_package(entries):
    zip_file = common.MakeTempFile(suffix='.zip')
    with zipfile.ZipFile(zip_file, 'w', allowZip64=True) as zip_fp:
      for entry in entries:
        zip_fp.writestr(
            entry,
            entry.replace('.', '-').upper(),
            zipfile.ZIP_STORED)
    return zip_file

  @staticmethod
  def _parse_property_files_string(data):
    result = {}
    for token in data.split(','):
      name, info = token.split(':', 1)
      result[name] = info
    return result

  def setUp(self):
    common.OPTIONS.no_signing = False

  def _verify_entries(self, input_file, tokens, entries):
    for entry in entries:
      offset, size = map(int, tokens[entry].split(':'))
      with open(input_file, 'rb') as input_fp:
        input_fp.seek(offset)
        if entry == 'metadata':
          expected = b'META-INF/COM/ANDROID/METADATA'
        elif entry == 'metadata.pb':
          expected = b'META-INF/COM/ANDROID/METADATA-PB'
        else:
          expected = entry.replace('.', '-').upper().encode()
        self.assertEqual(expected, input_fp.read(size))


if __name__ == '__main__':
  # We only want to run tests from the top level directory. Unfortunately the
  # pattern option of unittest.discover, internally using fnmatch, doesn't
  # provide a good API to filter the test files based on directory. So we do an
  # os walk and load them manually.
  test_modules = []
  base_path = os.path.dirname(os.path.realpath(__file__))
  for dirpath, _, files in os.walk(base_path):
    for fn in files:
      if dirpath == base_path and re.match('test_.*\\.py$', fn):
        test_modules.append(fn[:-3])

  test_suite = unittest.TestLoader().loadTestsFromNames(test_modules)

  # atest needs a verbosity level of >= 2 to correctly parse the result.
  unittest.TextTestRunner(verbosity=2).run(test_suite)
>>>>>>> BRANCH (fe6ad7 Merge "Version bump to RBT1.210107.001.A1 [core/build_id.mk])
