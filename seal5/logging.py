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
import socket
import os
import socketserver
import struct
import pickle
from typing import List, Tuple
import threading
from pathlib import Path

PROJECT_NAME = "seal5"
HOSTNAME = "localhost"
SEAL5_LOGGING_PORT = int(os.getenv("SEAL5_LOGGING_PORT", 0))
_log_server = None
_log_port = None
_logger = None


def resolve_log_level(value: str | int):
    return getattr(logging, value.upper()) if isinstance(value, str) else value


def get_formatter(minimal=False):
    """Returns a log formatter for one on two predefined formats."""
    if minimal:
        fmt = "[%(name)s::%(levelname)s] %(message)s"
    else:
        fmt = "%(asctime)s [%(name)s::%(levelname)s] (%(pathname)s::%(lineno)d %(message)s"
    formatter = logging.Formatter(fmt)
    return formatter


def get_logger(loggername: None | str = None, level=logging.DEBUG):
    
    server_reachable = False
    if _log_port is not None:
        try:
            with socket.create_connection((HOSTNAME, _log_port), timeout=0.2):
                server_reachable = True
        except OSError:
            server_reachable = False

    # --- Case 1: Logging server not reachable → local fallback logger fallback ---
    if not server_reachable:
        fallback_logger = logging.getLogger('fallback')  # fallback logger
        fallback_logger.setLevel(logging.DEBUG)

        # Ensure a StreamHandler exists only once
        if not any(isinstance(h, logging.StreamHandler) for h in fallback_logger.handlers):
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setFormatter(get_formatter(True))
            stream_handler.setLevel(logging.DEBUG)
            fallback_logger.addHandler(stream_handler)

        return fallback_logger

    logger = logging.getLogger(f"{PROJECT_NAME}.{loggername if loggername is not None else 'unknown'}")
    logger.handlers = []
    logger.setLevel(level=level)
    socket_handler = logging.handlers.SocketHandler(HOSTNAME, _log_port)
    logger.addHandler(socket_handler)
    return logger


def initialize_logging_server(
    logfiles: None | List[Tuple[Path | str, int]] = [
        ("log_debug.log", logging.DEBUG),
        ("log_info.log", logging.INFO),
    ], stream_log_level: int | str = logging.INFO,
):
    global _log_server, _log_port, _logger
    logger = logging.getLogger(PROJECT_NAME)
    _logger = logger
    # This should be the lowest value and not changeable since logger is the first filter
    logger.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(get_formatter(True))
    stream_handler.setLevel(resolve_log_level(stream_log_level))
    logger.addHandler(stream_handler)

    if logfiles is not None:
        for log_file, log_level in logfiles:
            file_handler = logging.FileHandler(log_file, "w")
            file_handler.setFormatter(get_formatter(False))
            file_handler.setLevel(resolve_log_level(log_level))
            logger.addHandler(file_handler)

    try:
        _log_server = LogRecordSocketReceiver(HOSTNAME, SEAL5_LOGGING_PORT)
        addr = _log_server.server_address
        assert len(addr) == 2
        _log_port = addr[1]
    except OSError as e:
        if e.errno == 98:  # Address already in use
            raise RuntimeError(
                "Initialization of logging Server not possible! Port Taken!"
            )
        else:
            raise  # rethrow unexpected errors

    thread = threading.Thread(target=_log_server.serve_forever)
    thread.daemon = True
    thread.start()
    print(f"Logger started on port {_log_port}")


def stop_logging_server():
    if _log_server is not None:
        print(f"Logger on port {_log_port} stopped.")
        _log_server.shutdown()
        _log_server.server_close()


def check_logging_server():
    # global _log_server, _log_port
    if _log_server is not None:
        assert _log_port is not None, "Logging server exists with undef port"
        return True
    return False


def update_log_level(console_level=None, file_level=None):
    """Set command line or file log level at runtime."""
    if _logger is not None:
        for handler in _logger.handlers[:]:
            if (
                isinstance(handler, (logging.FileHandler, logging.handlers.TimedRotatingFileHandler))
                and file_level is not None
            ):
                file_level = resolve_log_level(file_level)
                handler.setLevel(file_level)
            elif isinstance(handler, logging.StreamHandler) and console_level is not None:
                console_level = resolve_log_level(console_level)
                handler.setLevel(console_level)


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
    daemon_threads = True

    def __init__(self, host=None, port=None):
        assert host is not None, "Undefined host"
        assert port is not None, "Undefined port"
        super().__init__((host, port), LogRecordStreamHandler)


class Logger:
    """Proxy that initializes its logger only when first used."""

    def __init__(self, name=None):
        self._name = name
        self._logger = None

    def _get_logger(self):
        if self._logger is None:
            self._logger = get_logger(self._name)
        else:
            # replace fllabck logger with actual one of server is available
            if self._logger.name == "fallback" and check_logging_server():
                self._logger = get_logger(self._name)
        return self._logger

    def __getattr__(self, attr):
        return getattr(self._get_logger(), attr)

