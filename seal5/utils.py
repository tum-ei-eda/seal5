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
import shutil
import subprocess
import multiprocessing
from pathlib import Path
from typing import List, Callable, Optional

from seal5.logging import get_logger

logger = get_logger()


def copy(src, dest):
    shutil.copy(src, dest)


def is_populated(path):
    if not isinstance(path, Path):
        path = Path(path)
    return path.is_dir() and os.listdir(path.resolve())


def exec_getout(
    *args: List[str],
    ignore_output: bool = False,
    live: bool = False,
    print_func: Callable = print,
    handle_exit=None,
    err_func: Callable = logger.error,
    **kwargs,
) -> str:
    """Wrapper for running a program in a subprocess.

    Parameters
    ----------
    args : list
        The actual command.
    ignore_output : bool
        Do not get the stdout and stderr or the subprocess.
    live : bool
        Print the output line by line instead of only at the end.
    print_func : Callable
        Function which should be used to print sysout messages.
    err_func : Callable
        Function which should be used to print errors.
    kwargs: dict
        Arbitrary keyword arguments passed through to the subprocess.

    Returns
    -------
    out : str
        The command line output of the command
    """
    logger.debug("- Executing: %s", str(args))
    if ignore_output:
        assert not live
        subprocess.run(args, **kwargs, check=True)
        return None

    out_str = ""
    if live:
        with subprocess.Popen(
            args,
            **kwargs,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        ) as process:
            for line in process.stdout:
                new_line = line.decode(errors="replace")
                out_str = out_str + new_line
                print_func(new_line.replace("\n", ""))
            exit_code = None
            while exit_code is None:
                exit_code = process.poll()
            if handle_exit is not None:
                exit_code = handle_exit(exit_code)
            assert exit_code == 0, "The process returned an non-zero exit code {}! (CMD: `{}`)".format(
                exit_code, " ".join(list(map(str, args)))
            )
    else:
        p = subprocess.Popen([i for i in args], **kwargs, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out_str = p.communicate()[0].decode(errors="replace")
        exit_code = p.poll()
        print_func(out_str)
        if handle_exit is not None:
            exit_code = handle_exit(exit_code)
        if exit_code != 0:
            err_func(out_str)
        assert exit_code == 0, "The process returned an non-zero exit code {}! (CMD: `{}`)".format(
            exit_code, " ".join(list(map(str, args)))
        )

    return out_str


def cmake(src, *args, debug: Optional[bool] = None, use_ninja=False, cwd=None, **kwargs):
    if cwd is None:
        raise RuntimeError("Please always pass a cwd to cmake()")
    if isinstance(cwd, Path):
        cwd = str(cwd.resolve())
    extraArgs = []
    if debug is not None:
        buildType = "Debug" if debug else "Release"
        extraArgs.append("-DCMAKE_BUILD_TYPE=" + buildType)
    if use_ninja:
        extraArgs.append("-GNinja")
    cmd = ["cmake", str(src)] + extraArgs + list(args)
    return exec_getout(*cmd, cwd=cwd, **kwargs)




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
    return exec_getout(*cmd, cwd=cwd, **kwargs)
