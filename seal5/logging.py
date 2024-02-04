#
# Copyright (c) 2023 TUM Department of Electrical and Computer Engineering.
#
# This file is part of Seal5.
# See https://github.com/tum-ei-eda/seal5.git for further info.
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
#
"""Loging utilities for Seal5."""

import logging
import logging.handlers
import sys

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s]::%(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

initialized = False


def get_formatter(minimal=False):
    """Returns a log formatter for one on two predefined formats."""
    if minimal:
        fmt = "%(levelname)s - %(message)s"
    else:
        fmt = "[%(asctime)s]::%(pathname)s:%(lineno)d::%(levelname)s - %(message)s"
    formatter = logging.Formatter(fmt)
    return formatter


def get_logger():
    """Helper function which return the main seal5 logger while ensuring that is is properly initialized."""
    global initialized
    # root_logger = logging.getLogger()
    # root_logger.setLevel(logging.DEBUG)
    # root_logger.setLevel(logging.INFO)
    logger = logging.getLogger("seal5")
    # logger.setLevel(logging.DEBUG)
    if len(logger.handlers) == 0:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(get_formatter(minimal=True))
        # stream_handler.setLevel(logging.DEBUG)
        logger.addHandler(stream_handler)
        logger.propagate = False
        initialized = True
    return logger


def set_log_level(console_level=None, file_level=None):
    """Set command line log level at runtime."""
    # print("set_log_level", console_level, file_level)
    logger = logging.getLogger("seal5")
    for handler in logger.handlers[:]:
        # print("handler", handler, type(handler))
        if (
            isinstance(handler, (logging.FileHandler, logging.handlers.TimedRotatingFileHandler))
            and file_level is not None
        ):
            handler.setLevel(file_level)
            # print("NEWIF")
        elif isinstance(handler, logging.StreamHandler) and console_level is not None:
            handler.setLevel(console_level)
            # print("NEWELIF")
    logger.setLevel(logging.DEBUG)


def set_log_file(path, level=logging.DEBUG, rotate=False):
    """Enable logging to a file."""
    # print("set_log_file", level)
    logger = logging.getLogger("seal5")
    logger.setLevel(logging.DEBUG)
    if rotate:
        file_handler = logging.handlers.TimedRotatingFileHandler(filename=path, when="midnight", backupCount=30)
    else:
        file_handler = logging.FileHandler(path, mode="a")
    file_handler.setFormatter(get_formatter())
    # file_handler.setLevel(level)
    file_handler.setLevel(logging.DEBUG)
    for handler in logger.handlers[:]:
        if isinstance(handler, logging.FileHandler):
            logger.removeHandler(handler)
    logger.addHandler(file_handler)
