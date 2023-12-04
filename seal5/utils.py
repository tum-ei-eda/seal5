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
"""Seal5 utility functions."""
import os
import signal
import subprocess
import multiprocessing
from pathlib import Path

from seal5.logging import get_logger

logger = get_logger()


def is_populated(path):
    if not isinstance(path, Path):
        path = Path(path)
    return path.is_dir() and os.listdir(path.resolve())

def exec_getout(*args, live: bool = False, print_output: bool = True, handle_exit=None, prefix="", **kwargs) -> str:
    """Execute a process with the given args and using the given kwards as Popen arguments and return the output.

    Parameters
    ----------
    args
        The command to be executed.
    live : bool
        If the stdout should be updated in real time.
    print_output : bool
        Print the output at the end on non-live mode.

    Returns
    -------
    output
        The text printed to the command line.
    """
    logger.debug("- Executing: " + str(args))
    outStr = ""
    if live:
        process = subprocess.Popen([i for i in args], **kwargs, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        try:
            for line in process.stdout:
                new_line = prefix + line.decode(errors="replace")
                outStr = outStr + new_line
                print(new_line.replace("\n", ""))
            exit_code = None
            while exit_code is None:
                exit_code = process.poll()
            if handle_exit is not None:
                exit_code = handle_exit(exit_code)
            assert exit_code == 0, "The process returned an non-zero exit code {}! (CMD: `{}`)".format(
                exit_code, " ".join(list(map(str, args)))
            )
        except KeyboardInterrupt:
            logger.debug("Interrupted subprocess. Sending SIGINT signal...")
            pid = process.pid
            os.kill(pid, signal.SIGINT)

    else:
        try:
            p = subprocess.Popen([i for i in args], **kwargs, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            outStr = p.communicate()[0].decode(errors="replace")
            exit_code = p.poll()
            # outStr = p.stdout.decode(errors="replace")
            if print_output:
                logger.debug(prefix + outStr)
            if handle_exit is not None:
                exit_code = handle_exit(exit_code)
            if exit_code != 0:
                logger.error(outStr)
            assert exit_code == 0, "The process returned an non-zero exit code {}! (CMD: `{}`)".format(
                exit_code, " ".join(list(map(str, args)))
            )
        except KeyboardInterrupt:
            logger.debug("Interrupted subprocess. Sending SIGINT signal...")
            pid = p.pid
            os.kill(pid, signal.SIGINT)
        except subprocess.CalledProcessError as e:
            outStr = e.output.decode(errors="replace")
            logger.error(outStr)
            raise e

    return outStr


def cmake(src, *args, debug=False, use_ninja=False, cwd=None, **kwargs):
    if cwd is None:
        raise RuntimeError("Please always pass a cwd to cmake()")
    if isinstance(cwd, Path):
        cwd = str(cwd.resolve())
    buildType = "Debug" if debug else "Release"
    extraArgs = []
    extraArgs.append("-DCMAKE_BUILD_TYPE=" + buildType)
    if use_ninja:
        extraArgs.append("-GNinja")
    cmd = ["cmake", str(src)] + extraArgs + list(args)
    return exec_getout(*cmd, cwd=cwd, print_output=False, **kwargs)




def make(*args, threads=multiprocessing.cpu_count(), use_ninja=False, cwd=None, verbose=False, **kwargs):
    if cwd is None:
        raise RuntimeError("Please always pass a cwd to make()")
    if isinstance(cwd, Path):
        cwd = str(cwd.resolve())
    # TODO: make sure that ninja is installed?
    extraArgs = []
    tool = "ninja" if use_ninja else "make"
    extraArgs.append("-j" + str(threads))
    cmd = [tool] + extraArgs + list(args)
    return exec_getout(*cmd, cwd=cwd, print_output=False, **kwargs)
