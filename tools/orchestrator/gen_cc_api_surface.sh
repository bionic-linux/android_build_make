#!/bin/bash
set -euo pipefail

# Copyright (C) 2022 The Android Open Source Project
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


# Script that reads output json of a Bazel cc_api_surface target and
# 1. copies contribution files to multi-tree out/
# 2. generates Android.bp file for each contributing library
#
# Arguments
#  $1: outer tree out directory
#  $2: Bazel label of the cc_api_surface
#  $3: inner_tree root

OUT_DIR=$1
BAZEL_LABEL=$2
INNER_TREE=$3

# Use bazel query to determine output filepath of cc_api_surface
# Globals:
# Arguments:
#  $1: inner_tree_root (also the Bazel workspace root)
#  $2: label of the Bazel target
# Outputs:
#  Writes absolute filepath location to stdout, including inner_tree_root prefix
function bazel_output_filepath(){
  # Use prebuilt bazel directly instead of the bazel() function added by
  # build/make/envsetup.sh
  # The shell function runs the prebuilt bazel using --config=bp2build, and
  # depends on values generated from Soong
  # The api surfaces do not have any dependencies on Soong, and therefore can be
  # built/queried in standalone/pure mode
  output=$(cd $1 && \
    prebuilts/bazel/linux-x86_64/bazel aquery --output=text $2 2>/dev/null | \
    grep Outputs | \
    awk '{print $NF}' | \
    sed 's/\[//g' | \
    sed 's/\]//g' # Extract substring between [] brackets
  )
  echo $1/$output
}

# Helper function to copy multiple files to out directory
# Globals:
# Arguments:
#  $1: target location in OUT_DIR
#  $2: inner_tree_root
#  $3-n: source files to copy, relative to workspace root
# Outputs:
#  None
function copy_files(){
  out_location=$1
  shift;
  inner_tree=$1
  shift;
  mkdir -p $out_location
  (cd $inner_tree && cp -t $out_location $@)
}

# Generates an Android.bp file from a template
# Globals:
# Arguments:
#  $1: name of the stub library
#  $2: name of the api surface
#  $3: name of the symbol file
#  $4: first version
# Outputs:
#  Writes the substitued template to stdout
function generate_bp_from_template(){
  header_module_name=$1_headers
cat << EOF
// AUTOGENERATED: DO NOT EDIT
cc_stub_library {
  name: "$1",
  api_surface_name: "$2",
  symbol_file: "$3",
  first_version: "$4",
}

cc_library_headers {
  name: "$header_module_name",
  export_include_dirs: [
      "include",
  ],
}
EOF
}

# Determine output filepath from bazel label
api_surface_output_filepath=$(bazel_output_filepath $INNER_TREE $BAZEL_LABEL)

# Read metadata from json
# Use -c compact output to enable iteration in a for loop
api_surface_name=$(jq -rc .name $api_surface_output_filepath)
api_contributions=$(jq -rc .contributions[] $api_surface_output_filepath)

# Loop over api_contribtions
for api_contribution in ${api_contributions}; do
  api_library_name=$(echo $api_contribution | jq -rc .name)
  first_version=$(echo $api_contribution | jq -rc .first_version)
  output_directory_for_contributions=$OUT_DIR/$api_surface_name/$api_library_name

  # Copy headers to $output_directory_for_contributions/include
  headers=$(echo $api_contribution | jq -rc .headers_filepath[])
  copy_files $output_directory_for_contributions/include $INNER_TREE $headers

  # Copy symbol_file to $output_directory_for_contributions
  symbol_file=$(echo $api_contribution | jq -rc .symbol_filepath)
  copy_files $output_directory_for_contributions $INNER_TREE $symbol_file

  # Generate Android.bp in $output_directory_for_contributions
  generate_bp_from_template $api_library_name $api_surface_name $symbol_file $first_version > $output_directory_for_contributions/Android.bp
done
