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


import argparse
import logging
import os
import sys
import signal
import time
import tempfile

from edit_monitor import daemon_manager


def create_arg_parser():
    """Creates an instance of the default ToolEventLogger arg parser."""

    parser = argparse.ArgumentParser(
        description='Build and upload logs for Android dev tools',
        add_help=True,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        '--path',
        type=str,
        required=True,
        help='directories to monitor',
    )

    return parser


def configure_logging():
    root_logging_dir = tempfile.mkdtemp(prefix='edit_monitor_')
    _, log_path = tempfile.mkstemp(dir=root_logging_dir, suffix='.log')

    log_fmt = '%(asctime)s %(filename)s:%(lineno)s:%(levelname)s: %(message)s'
    date_fmt = '%Y-%m-%d %H:%M:%S'
    logging.basicConfig(
        filename=log_path, level=logging.DEBUG, format=log_fmt, datefmt=date_fmt
    )
    print(f"logging file to {log_path}")


def main(argv: list[str]):
    args = create_arg_parser().parse_args(argv[1:])
    dm = daemon_manager.DaemonManager(binary_path=argv[0])
    try:
        dm.start()
        # dm.monitor_daemon()
        time.sleep(1)
    except Exception as e:
        logging.error(f"excpetion raised when runn daemon, error: {e}")
    finally:
        dm.stop()


if __name__ == "__main__":
    configure_logging()
    main(sys.argv)
