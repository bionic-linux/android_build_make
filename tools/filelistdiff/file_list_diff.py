# Copyright (C) 2024 The Android Open Source Project
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

import sys

def find_unique_items(kati_installed_files, soong_installed_files, allowlist):
    with open(kati_installed_files, 'r') as kati_list_file, \
            open(soong_installed_files, 'r') as soong_list_file, \
            open(allowlist, 'r') as allowlist_file:
        kati_files = set(kati_list_file.read().split())
        soong_files = set(soong_list_file.read().split())
        allowed_files = set(filter(lambda x: len(x), map(lambda x: x.lstrip().split('#',1)[0].rstrip() , allowlist_file.read().split('\n'))))

    def is_unknown_diff(filepath):
        for allowed_file in allowed_files:
            if allowed_file == filepath:
                return False
        return True

    unique_in_kati = set(filter(is_unknown_diff, kati_files - soong_files))
    unique_in_soong = set(filter(is_unknown_diff, soong_files - kati_files))

    if unique_in_kati:
        print('KATI only module(s):')
        for item in sorted(unique_in_kati):
            print(item)

    if unique_in_soong:
        if unique_in_kati:
            print('')
        print('SOONG only module(s):')
        for item in sorted(unique_in_soong):
            print(item)

    if unique_in_kati or unique_in_soong:
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(f'Usage: file_list_diff <kati_installed_files_list> <soong_installed_files_list> <allowlist>')

    kati_installed_files = sys.argv[1]
    soong_installed_files = sys.argv[2]
    allowlist = sys.argv[3]
    find_unique_items(kati_installed_files, soong_installed_files, allowlist)