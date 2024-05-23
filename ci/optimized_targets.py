#
# Copyright 2024, The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from abc import ABC


class OptimizedBuildTarget(ABC):

  def __init__(self, build_context, args):
    self.build_context = build_context
    self.args = args

  def get_build_targets(self):
    pass

  def package_outputs(self):
    pass


class NullOptimizer(OptimizedBuildTarget):

  def __init__(self, target):
    self.target = target

  def get_build_targets(self):
    return {self.target}

  def package_outputs():
    pass


def get_target_optimizer(target, enabled_flag, build_context, optimizer):
  if enabled_flag in build_context['enabled_build_features']:
    return optimizer

  return NullOptimizer(target)


# To be written as:
#    'target': lambda target, build_context, args: get_target_optimizer(
#        target,
#        'target_enabled_flag',
#        build_context,
#        TargetOptimizer(build_context, args),
#    )
OPTIMIZED_BUILD_TARGETS = dict()
