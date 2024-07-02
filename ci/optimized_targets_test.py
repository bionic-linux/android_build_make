"""TODO(lucafarsi): DO NOT SUBMIT without either providing a detailed docstring or

removing it altogether.
"""

import re
import unittest
import optimized_targets


class OptimizedTargetsTest(unittest.TestCase):

  def test_give_me_a_name(self):
    self.assertTrue(
        re.match(re.compile('.*general-tests.zip'), 'general-tests.zip')
    )

  def test_optimization_flag_enabled_target_optimized(self):
    build_context = self._get_build_context()

    optimizer = self._get_target_optimizer(build_context)

    self.assertTrue(isinstance(optimizer, self.TestOptimizedTarget))

  def test_optimization_flag_not_enabled_target_not_optimized(self):
    build_context = self._get_build_context()
    build_context['enabledBuildFeatures'].remove('test-target-optimized')

    optimizer = self._get_target_optimizer(build_context)

    self.assertTrue(isinstance(optimizer, optimized_targets.NullOptimizer))

  class TestOptimizedTarget(optimized_targets.OptimizedBuildTarget):
    pass

  def _get_build_context(self):
    return {
        'enabledBuildFeatures': ['optimized_build', 'test-target-optimized'],
    }

  def _get_target_optimizer(self, build_context):
    return optimized_targets.get_target_optimizer(
        'test_target',
        'test-target-optimized',
        build_context,
        self.TestOptimizedTarget(build_context, []),
    )


class ExcludeUnusedTargetOptimizerTest(unittest.TestCase):

  def test_target_output_used_target_built(self):
    optimizer = self._get_target_optimizer(self._get_build_context())

    expected_targets = {'test_target'}

    self.assertEqual(optimizer.get_build_targets(), expected_targets)

  def test_target_regex_used_target_built(self):
    build_context = self._get_build_context()
    build_context['testContext']['testInfos'][0]['extraOptions'][0][
        'values'
    ] = ['.*output.zip.*']
    optimizer = self._get_target_optimizer(build_context)

    expected_targets = {'test_target'}

    self.assertEqual(optimizer.get_build_targets(), expected_targets)

  def test_target_output_not_used_target_not_built(self):
    build_context = self._get_build_context()
    build_context['testContext']['testInfos'][0]['extraOptions'] = []
    optimizer = self._get_target_optimizer(build_context)

    expected_targets = set()

    self.assertEqual(optimizer.get_build_targets(), expected_targets)

  def _get_target_optimizer(self, build_context):
    return optimized_targets.ExcludeUnusedTargetOptimizer(
        build_context,
        [],
        'test_target',
        optimized_targets.NullOptimizer('test_target'),
        self._get_target_to_outputs(),
    )

  def _get_build_context(self):
    return {
        'enabledBuildFeatures': ['optimized_build', 'test-target-optimized'],
        'testContext': {
            'testInfos': [
                {
                    'name': 'atp_test',
                    'target': 'test_target',
                    'branch': 'branch',
                    'extraOptions': [{
                        'key': 'additional-files-filter',
                        'values': ['test_target_output.zip'],
                    }],
                    'command': '/tf/command',
                    'extraBuildTargets': [
                        'extra_build_target',
                    ],
                },
            ],
        },
    }

  def _get_target_to_outputs(self):
    return {'test_target': ['test_target_output.zip']}


if __name__ == '__main__':
  unittest.main()
