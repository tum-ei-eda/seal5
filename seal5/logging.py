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
import socketserver
import struct
import pickle
from typing import List, Tuple
import threading

PROJECT_NAME = "seal5"
HOSTNAME = "localhost"
LOGGINGPORT = 9020


def get_formatter(minimal=False):
    """Returns a log formatter for one on two predefined formats."""
    if minimal:
        fmt = "[%(name)s::%(levelname)s] %(message)s"
    else:
        fmt = "%(asctime)s [%(name)s::%(levelname)s] (%(pathname)s::%(lineno)d %(message)s"
    formatter = logging.Formatter(fmt)
    return formatter


def get_logger(loggername: None | str = None, level=logging.DEBUG):
    name = PROJECT_NAME if loggername is None else f"{PROJECT_NAME}.{loggername}"
    logger = logging.getLogger(name)
    logger.handlers = []
    logger.setLevel(level=level)
    socket_handler = logging.handlers.SocketHandler(HOSTNAME, LOGGINGPORT)
    logger.addHandler(socket_handler)
    return logger


def initialize_logging_server(
    logfiles: None | List[Tuple[str, int]] = [
        ("log_debug.log", logging.DEBUG),
        ("log_info.log", logging.INFO),
    ],
):
    logger = logging.getLogger(PROJECT_NAME)
    logger.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(get_formatter(True))
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)

    if logfiles is not None:
        for log_file, log_level in logfiles:
            file_handler = logging.FileHandler(log_file, "w")
            file_handler.setFormatter(get_formatter(False))
            file_handler.setLevel(log_level)
            logger.addHandler(file_handler)

    try:
        server = LogRecordSocketReceiver()
    except OSError as e:
        if e.errno == 98:  # Address already in use
            logging.warning("Log listener is expected to be only initialized once!")
            return None  # Be careful on server.shutdown()
        else:
            raise  # rethrow unexpected errors

    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    print(f"Logger started on port {LOGGINGPORT}")

    return server


# --- Server (listener) that receives LogRecords ---
class LogRecordStreamHandler(socketserver.StreamRequestHandler):
    def handle(self):
        while True:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack(">L", chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk += self.connection.recv(slen - len(chunk))
            record = logging.makeLogRecord(pickle.loads(chunk))
            logger = logging.getLogger(record.name)
            # The logger is sent, if it holds a socket_handler it will answer ending in a loop
            socket_handlers = [
                h
                for h in logger.handlers
                if isinstance(h, logging.handlers.SocketHandler)
            ]
            for h in socket_handlers:
                logger.removeHandler(h)
            logger.handle(record)


class LogRecordSocketReceiver(socketserver.ThreadingTCPServer):
    allow_reuse_address = True

    def __init__(self, host=HOSTNAME, port=LOGGINGPORT):
        super().__init__((host, port), LogRecordStreamHandler)
