from enum import Enum
import time
import metrics_pb2


class MetricsAgent:
  _instance = None

  def __init__(self):
    raise RuntimeError(
        'MetricsAgent cannot be instantialized, use instance() instead'
    )

  @classmethod
  def instance(cls):
    if not cls._instance:
      cls._instance = cls.__new__(cls)
      cls._instance._proto = metrics_pb2.OptimizedBuildMetrics()
      cls._instance._init_proto()
      cls._instance._target_results = dict()

    return cls._instance

  def _init_proto(self):
    self._proto.analysis_perf.name = 'Optimized build analysis time.'
    self._proto.packaging_perf.name = 'Optimized build total packaging time.'

  def analysis_start(self):
    self._proto.analysis_perf.start_time = time.time_ns()

  def analysis_end(self):
    self._proto.analysis_perf.real_time = (
        time.time_ns() - self._proto.analysis_perf.start_time
    )

  def packaging_start(self):
    self._proto.packaging_perf.start_time = time.time_ns()

  def packaging_end(self):
    self._proto.packaging_perf.real_time = (
        time.time_ns() - self._proto.packaging_perf.start_time
    )

  def report_unoptimized_target(self, name: str, optimization_rationale: str):
    target_result = metrics_pb2.OptimizedBuildMetrics.TargetOptimizationResult()
    target_result.name = name
    target_result.optimization_rationale = optimization_rationale
    target_result.optimized = False
    self._target_results[name] = target_result

  def target_packaging_start(self, name: str):
    target_result = metrics_pb2.OptimizedBuildMetrics.TargetOptimizationResult()
    target_result.name = name
    target_result.optimized = True
    target_result.packaging_perf.start_time = time.time_ns()
    self._target_results[name] = target_result

  def target_packaging_end(self, name: str):
    target_result = self._target_results.get(name)
    target_result.packaging_perf.real_time = (
        time.time_ns() - target_result.packaging_perf.start_time
    )

  def add_target_artifact(
      self,
      target_name: str,
      artifact_name: str,
      size: int,
      included_modules: set[str],
  ):
    target_result = self.target_results.get(target_name)
    artifact = (
        metrics_pb2.OptimizedBuildMetrics.TargetOptimizationResult.OutputArtifact()
    )
    artifact.name = artifact_name
    artifact.size = size
    for module in included_modules:
      artifact.included_modules.add(module)
    target_result.output_artifacts.add(artifact)

  def end_reporting(self):
    soong_metrics_proto = metrics_pb2.MetricsBase()
    with open('out/dist/logs/soong_metrics', 'rb') as f:
      pass
      soong_metrics_proto.ParseFromString(f.read())
    soong_metrics_proto.optimized_build_metrics = self._proto
    with open('out/dist/logs/soong_metrics', 'wb') as f:
      f.write(soong_metrics_proto.serializeToString())
