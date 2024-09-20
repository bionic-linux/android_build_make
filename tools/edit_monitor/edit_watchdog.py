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


import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')
from datetime import datetime
#import psutil
import importlib
from pathlib import Path
from atest.proto import clientanalytics_pb2
from proto import edit_event_pb2
from atest.metrics import clearcut_client
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer
import argparse
import datetime
import getpass
import logging
import os
import platform
import sys
import tempfile
import uuid
import time
import threading
import signal
import multiprocessing
import subprocess
import hashlib

from atest.metrics import clearcut_client
from atest.proto import clientanalytics_pb2
#from proto import tool_event_pb2



# PID_file = "/tmp/edit_monitor/edit_monitor.pid"
PID_DIR = "/tmp/edit_monitor"
BINARY_FILE = "./tools/asuite/edit_monitor"
BLOCK_SIGN = "/tmp/edit_monitor_block"
# LOG_SOURCE = 2395
# import watchdog
# from watchdog.events import LoggingEventHandler


_DEFAULT_FLUSH_INTERVAL_SEC = 60  # 1 Minute
LOG_SOURCE = 2395


class ClearcutEventHandler(PatternMatchingEventHandler):
  def __init__(self, path, patterns=None, ignore_patterns=None,
               exclude_directories=None, ignore_hidden_files=True, log_buffer_size=20,
               flush_interval_sec=1, client=None
               ):

    super().__init__(
        patterns=patterns, ignore_patterns=ignore_patterns,
        ignore_directories=True)
    self.path = path
    self.ignore_hidden_files = ignore_hidden_files
    self.log_buffer_size = log_buffer_size
    self.flush_interval_sec = flush_interval_sec
    self.pending_events = []
    self._scheduled_flush_thread = None
    self._pending_events_lock = threading.Lock()
    self.exclude_directories = exclude_directories
    if not client:
      self.clearcut_client = clearcut_client.Clearcut(
          LOG_SOURCE, buffer_size=log_buffer_size, flush_interval_sec=flush_interval_sec)
    else:
      self.client = client
    self.user_name = getpass.getuser()
    self.host_name = platform.node()
    self.source_root = os.environ.get('ANDROID_BUILD_TOP', '')
    self.last_edit = time.time()

  def flushall(self):
    print("flushing all pending events.")
    if self._scheduled_flush_thread:
      self._scheduled_flush_thread.cancel()
      self._schedule_flush_thread(0)

  def is_hidden_file(self, filepath):
    # Check if the file itself is hidden
    try:
      if os.path.basename(filepath).startswith('.'):
        return True

      # Check if any parent directory is hidden
      while filepath != '/' and filepath != ".":
        if os.path.basename(filepath).startswith('.'):
          return True
        filepath = os.path.dirname(filepath)
    except FileNotFoundError:
      print("file already delted.")
      return True

    return False

  def is_under_git_project(self, filepath):
    try:
      current_dir = os.path.dirname(filepath)
      print(f"current_dir: {current_dir}")

      while True:
          print(f"current_dir: {current_dir}")
          if os.path.exists(os.path.join(current_dir, ".git")):
            return True
          if current_dir == self.path:
            break
          # Move to the parent directory
          current_dir = os.path.dirname(current_dir)
    except FileNotFoundError:
      print("file already deleted 2")
      return True

    return False

  def log_edit_event(self, event, event_type, event_time):
    try:
      if self.ignore_hidden_files and self.is_hidden_file(event.src_path):
        print(f"ignore hidden file: {event.src_path}")
        return

      # if self.is_under_exclude_directory(event.src_path):
      #  print(f"ignore file {event.src_path} under exclude directory {self.exclude_directories}")
      #  return

      if not self.is_under_git_project(event.src_path):
        print(
            f"ignore file {event.src_path} which does not belong to a git project")
        return
    except Exception as e:
      print("something unexpected happened during file checking, drop evnets")
      return

    print(f"{event_type}: {event.src_path}")
    event_proto = edit_event_pb2.ToolEvent(
        tool_tag='EDIT',
        invocation_id='0',
        user_name=self.user_name,
        host_name=self.host_name,
        source_root=self.source_root,
    )
    event_proto.invocation_started.CopyFrom(
        edit_event_pb2.ToolEvent.InvocationStarted(
            command_args=event_type,
            cwd=event.src_path,
        )
    )
    with self._pending_events_lock:
      self.pending_events.append((event_proto, event_time))
    if not self._scheduled_flush_thread:
      self._schedule_flush_thread(self.flush_interval_sec)

  def _schedule_flush_thread(self, time_from_now):
    # print(f'Scheduling thread to run in {time_from_now} seconds')
    self._scheduled_flush_thread = threading.Timer(time_from_now, self._flush)
    self._scheduled_flush_thread.start()

  def _flush(self):
    """Flush buffered events to Clearcut.

    If the sent request is unsuccessful, the events will be appended to
    buffer and rescheduled for next flush.
    """
    with self._pending_events_lock:
      self._scheduled_flush_thread = None
      events = self.pending_events
      self.pending_events = []

    pending_events_size = len(events)
    if pending_events_size > self.log_buffer_size:
      print(f"got {pending_events_size} events in {self.flush_interval_sec} seconds, consider non-human editing, dropping the events")
      return

    self._log_clearcut_event(events)
    # log_request = self._serialize_events_to_proto(events)
    # self._send_to_clearcut(log_request.SerializeToString())
    print(f"sent {pending_events_size} events")

  def _log_clearcut_event(self, edit_events):
    for event_proto, event_time in edit_events:
      log_event = clientanalytics_pb2.LogEvent(
          event_time_ms=int(event_time * 1000),
          source_extension=event_proto.SerializeToString(),
      )
      self.clearcut_client.log(log_event)

  def on_moved(self, event):
    # pass
    self.last_edit = time.time()
    self.log_edit_event(event, "Moved", time.time())

  def on_created(self, event):
    # pass
    self.last_edit = time.time()
    self.log_edit_event(event, "Created", time.time())

  def on_deleted(self, event):
    # pass
    self.last_edit = time.time()
    self.log_edit_event(event, "Deleted", time.time())

  def on_modified(self, event):
    # pass
    self.last_edit = time.time()
    # if event.src_path == BINARY_FILE:
    #  print ("binary file modified, restart the monitor")
    #  print ("executable: ", sys.argv[0])
    # kill_existing_instance(True)
    #  binary_path = sys.argv[0]
    #  with open(PID_file, "r") as f:
    #    pid = int(f.read())
    #  if pid == os.getpid():
    #    os.remove(PID_file)
    #  try:
    #    os.execv(binary_path, sys.argv)
    #  except OSError as e:
    #    print(f"Error restarting process: {e}")
    #    sys.exit(1)  # Indicate an error occurred

    # else:
    self.log_edit_event(event, "Modified", time.time())

  def get_last_edit(self):
    return self.last_edit


def start_daemon(path, patterns, pid):
  event_handler = ClearcutEventHandler(path, patterns)
  observer = Observer()
  print("Starting observer")
  observer.schedule(event_handler, path, recursive=True)
  observer.start()
  print("Observer started")
  # print ("executable: ", sys.argv[0])
  try:
    while True:
      if time.time() > event_handler.get_last_edit() + 6000:
        print(
            "\033[32;40mNo edit event detectd in the past 6000 s, restart the monitor.\033[0m")
        os.kill(pid, signal.SIGHUP)
        # sys.exit(0)
      time.sleep(1)
  finally:
    print("in daemon cleanup")
    event_handler.flushall()
    observer.stop()
    observer.join()
