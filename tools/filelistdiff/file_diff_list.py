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

def find_unique_items(kati_installed_files, soong_installed_files):
    with open(kati_installed_files, 'r') as file1, open(soong_installed_files, 'r') as file2:
        set1 = set(file1.read().split())
        set2 = set(file2.read().split())

    unique_in_kati = set1 - set2
    unique_in_soong = set2 - set1

    if unique_in_kati:
        print(f"KATI_Only:")
        for item in sorted(unique_in_kati):
            print(item)

    if unique_in_soong:
        print(f"\nSOONG_Only:")
        for item in sorted(unique_in_soong):
            print(item)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: file_diff_list <kati_installed_files_list> <soong_installed_files_list>")
        sys.exit(1)

    kati_installed_files = sys.argv[1]
    soong_installed_files = sys.argv[2]
    find_unique_items(kati_installed_files, soong_installed_files)