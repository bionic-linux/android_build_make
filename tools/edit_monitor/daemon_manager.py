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


import hashlib
import logging
import multiprocessing
import os
import pathlib
import signal
import subprocess
import sys
import tempfile
import time


DEFAULT_PROCESS_TERMINATION_TIMEOUT_SECONDS = 1
DEFAULT_PROCESS_TERMINATION_TIMEOUT_SECONDS = 1
DEFAULT_MONITOR_INTERVAL_SECONDS = 5
DEFAULT_MEMORY_USAGE_THRESHOLD = 2000
DEFAULT_CPU_USAGE_THRESHOLD = 200
DEFAULT_RESTART_INTERVAL_SECONDS = 60 * 60 * 24


def default_daemon_target():
  """Place holder for the default daemon target."""
  print("default daemon target")
  time.sleep(10)


class DaemonManager:
  """Class to manage and monitor the daemon run as a subprocess."""

  def __init__(
      self,
      binary_path: str,
      daemon_target: callable = default_daemon_target,
      daemon_args: tuple = (),
  ):
    self.binary_path = binary_path
    self.daemon_target = daemon_target
    self.daemon_args = daemon_args

    self.pid = os.getpid()
    self.daemon_process = None

    self.max_memory_usage = 0
    self.max_cpu_usage = 0

    pid_file_dir = pathlib.Path(tempfile.gettempdir()).joinpath("edit_monitor")
    pid_file_dir.mkdir(parents=True, exist_ok=True)
    self.pid_file_path = self._get_pid_file_path(pid_file_dir)

  def start(self):
    """Writes the pidfile and starts the daemon proces."""
    try:
      self._stop_any_existing_instance()
      self._write_pid_to_pidfile()
      self._start_daemon_process()
    except Exception as e:
      logging.exception("Failed to start daemon manager with error %s", e)

  def monitor_daemon(
      self,
      interval: int = DEFAULT_MONITOR_INTERVAL_SECONDS,
      memory_threshold: float = DEFAULT_MEMORY_USAGE_THRESHOLD,
      cpu_threshold: float = DEFAULT_CPU_USAGE_THRESHOLD,
      restart_interval: int = DEFAULT_RESTART_INTERVAL_SECONDS,
  ):
    logging.info("start monitoring daemon process %d.", self.daemon_process.pid)
    next_restart_time = time.time() + restart_interval
    while self.daemon_process.is_alive():
      if time.time() > next_restart_time:
        self.restart()
      try:
        memory_usage = self._get_process_memory_percent(self.daemon_process.pid)
        self.max_memory_usage = max(self.max_memory_usage, memory_usage)

        cpu_usage = self._get_process_cpu_percent(self.daemon_process.pid)
        self.max_cpu_usage = max(self.max_cpu_usage, cpu_usage)

        time.sleep(interval)
      except Exception as e:
        logging.warning("Failed to monitor daemon process with error: %s", e)

      if (
          self.max_memory_usage > memory_threshold
          or self.max_cpu_usage > cpu_threshold
      ):
        logging.error(
            "Daemon process is consuming too much resource, killing..."
        ),
        self._terminate_process(self.daemon_process.pid)

    logging.info(
        "Daemon process %d terminated. Max memory usage: %f, Max cpu"
        " usage: %f.",
        self.daemon_process.pid,
        self.max_memory_usage,
        self.max_cpu_usage,
    )

  def stop(self):
    """Stops the daemon process and removes the pidfile."""

    logging.debug("in daemon manager cleanup.")
    try:
      if self.daemon_process and self.daemon_process.is_alive():
        self._terminate_process(self.daemon_process.pid)
      self._remove_pidfile()
      logging.debug("Successfully stopped daemon manager.")
    except Exception as e:
      logging.exception("Failed to stop daemon manager with error %s", e)

  def restart(self):
    logging.debug("Restarting process based on binary %s.", self.binary_path)

    # Stop the current daemon manager first.
    self.stop()

    # If the binary no longer exists, exit directly.
    if not os.path.exists(self.binary_path):
      logging.info("binary %s no longer exists, exiting.", self.binary_path)
      sys.exit(0)

    try:
      os.execv(self.binary_path, sys.argv)
    except OSError as e:
      logging.exception("Failed to restart process with error: %s.", e)
      sys.exit(1)  # Indicate an error occurred

  def _stop_any_existing_instance(self):
    if not self.pid_file_path.exists():
      logging.info("No existing instances.")
      return

    ex_pid = self._read_pid_from_pidfile()

    if ex_pid:
      logging.info("Found another instance with pid %d.", ex_pid)
      self._terminate_process(ex_pid)
      self._remove_pidfile()

  def _read_pid_from_pidfile(self):
    with open(self.pid_file_path, "r") as f:
      return int(f.read().strip())

  def _write_pid_to_pidfile(self):
    """Creates a pidfile and writes the current pid to the file.

    Raise FileExistsError if the pidfile already exists.
    """
    try:
      # Use the 'x' mode to open the file for exclusive creation
      with open(self.pid_file_path, "x") as f:
        f.write(f"{self.pid}")
    except FileExistsError as e:
      # This could be caused due to race condition that a user is trying
      # to start two edit monitors at the same time. Or because there is
      # already an existing edit monitor running and we can not kill it
      # for some reason.
      logging.exception("pidfile %s already exists.", self.pid_file_path)
      raise e

  def _start_daemon_process(self):
    """Starts a subprocess to run the daemon."""
    p = multiprocessing.Process(
        target=self.daemon_target, args=self.daemon_args
    )
    p.start()

    logging.info("Start subprocess with PID %d", p.pid)
    self.daemon_process = p

  def _terminate_process(
      self, pid: int, timeout: int = DEFAULT_PROCESS_TERMINATION_TIMEOUT_SECONDS
  ):
    """Terminates a process with given pid.

    It first sends a SIGTERM to the process to allow it for proper
    termination with a timeout. If the process is not terminated within
    the timeout, kills it forcefully.
    """
    try:
      os.kill(pid, signal.SIGTERM)
      if not self._wait_for_process_terminate(pid, timeout):
        logging.warning(
            "Process %d not terminated within timeout, try force kill", pid
        )
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
      logging.info("Process with PID %d not found (already terminated)", pid)

  def _wait_for_process_terminate(self, pid: int, timeout: int) -> bool:
    start_time = time.time()

    while time.time() < start_time + timeout:
      if not self._is_process_alive(pid):
        return True
      time.sleep(1)

    logging.error("Process %d not terminated within %d seconds.", pid, timeout)
    return False

  def _is_process_alive(self, pid: int) -> bool:
    try:
      output = subprocess.check_output(
          ["ps", "-p", str(pid), "-o", "state="], text=True
      ).strip()
      state = output.split()[0]
      return state != "Z"  # Check if the state is not 'Z' (zombie)
    except subprocess.CalledProcessError:
      # Process not found (already dead).
      return False
    except (FileNotFoundError, OSError, ValueError) as e:
      logging.warning(
          "Unable to check the status for process %d with error: %s.", pid, e
      )
      return True

  def _remove_pidfile(self):
    try:
      os.remove(self.pid_file_path)
    except FileNotFoundError:
      logging.info("pid file %s already removed.", self.pid_file_path)

  def _get_pid_file_path(self, pid_file_dir: pathlib.Path) -> pathlib.Path:
    """Generates the path to store the pidfile.

    The file path should have the format of "/tmp/edit_monitor/xxxx.lock"
    where xxxx is a hashed value based on the binary path that starts the
    process.
    """
    hash_object = hashlib.sha256()
    hash_object.update(self.binary_path.encode("utf-8"))
    pid_file_path = pid_file_dir.joinpath(hash_object.hexdigest() + ".lock")
    logging.info("pid_file_path: %s", pid_file_path)

    return pid_file_path

  def _get_process_memory_percent(self, pid) -> float:
    try:
      memory_usage = self._get_resource_usage_info_from_pidstat("memory", pid)
      return int(memory_usage) / 1024  # Covert to MB
    except (subprocess.CalledProcessError, IndexError, ValueError) as e:
      logging.exception("Failed to get memory usage with error: %d", e)
      raise e

  def _get_process_cpu_percent(self, pid) -> float:
    try:
      cpu_usage = self._get_resource_usage_info_from_pidstat("cpu", pid)
      return float(cpu_usage)
    except (subprocess.CalledProcessError, IndexError, ValueError) as e:
      logging.exception("Failed to get CPU usage with error: %s", e)
      raise e

  def _get_resource_usage_info_from_pidstat(
      self, resource_type: str, pid
  ) -> str:
    cmd = []
    keyword = ""
    if resource_type == "memory":
      cmd = ["pidstat", "-r", "-p", str(pid), "1", "1"]
      keyword = "RSS"
    elif resource_type == "cpu":
      cmd = ["pidstat", "-u", "-p", str(pid), "1", "1"]
      keyword = "%CPU"

    output = subprocess.check_output(cmd, text=True)
    index = None
    for line in output.splitlines():
      parts = line.split()
      if keyword in parts:
        index = parts.index(keyword)
      if index and str(pid) in parts:
        return parts[index]
