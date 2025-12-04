#
# Copyright (c) 2025 TUM Department of Electrical and Computer Engineering.
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
import os
import inspect
import hashlib
import json
import threading
from pathlib import Path

import git
import psutil

from seal5.logging import Logger


logger = Logger("build_cache")


fuseoverlayfs = None


def init_fuseoverlayfs():
    global fuseoverlayfs
    if fuseoverlayfs is None:
        from fuseoverlayfs import FuseOverlayFS

        fuseoverlayfs = FuseOverlayFS.init()


def hash_arguments():
    args = json.dumps(
        inspect.currentframe().f_back.f_locals, sort_keys=True, default=lambda obj: f"<{obj.__class__.__name__}>"
    )
    logger.info("Build arguments: %s", args)
    return hashlib.sha1(args.encode()).hexdigest()


def get_patch_id(repo_path, base_commit, target_commit="HEAD"):
    repo = git.Repo(repo_path)
    r_fd, w_fd = os.pipe()
    t = threading.Thread(
        target=lambda: repo.git.execute(
            ["git", "diff", base_commit, target_commit], output_stream=os.fdopen(w_fd, "wb")
        )
    )
    t.start()
    # Run 'git patch-id' by piping the diff to it
    with os.fdopen(r_fd, "rb") as r:
        # patch_id will be a string like: '<patch-id> <zeroes or commit-hash>'
        patch_id = repo.git.execute(["git", "patch-id"], istream=r).split()[0]
    t.join()
    return patch_id


def combine_hashes(first, second):
    return hashlib.sha1(bytes.fromhex(first) + b":" + bytes.fromhex(second)).hexdigest()


def get_mount_info(mountpoint):
    for proc in psutil.process_iter(["name", "cmdline"]):
        try:
            # Look for fuse-overlayfs process
            if "fuse-overlayfs" in proc.info["name"]:
                cmdline = proc.info["cmdline"]
                # Check if the mountpoint is in the command line
                if any(str(mountpoint) in arg for arg in cmdline):
                    # Look for upperdir argument
                    for arg in cmdline:
                        if arg.startswith("upperdir="):
                            return Path(arg.split("=", 1)[1]).resolve().parent
        except (psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return None


def get_lower_dirs(directory, default=None):
    try:
        return [Path(line.strip()) for line in (directory / "lowerdirs.txt").read_text().splitlines() if line.strip()]
    except FileNotFoundError:
        return default if default is not None else []


def save_lower_dirs(directory, lower_dirs):
    (directory / "lowerdirs.txt").write_text("\n".join(map(str, lower_dirs)))


def query_build_cache(build_hash, build_dir, cache_dir):
    init_fuseoverlayfs()

    mount_info = get_mount_info(build_dir)
    logger.debug("Mount info: %s", mount_info)
    if mount_info is not None:
        logger.debug("Mount info: %s", mount_info.name)
    logger.debug("Hash: %s", build_hash)
    overlay_dir = cache_dir / build_hash
    work_dir = cache_dir / "work"
    empty_dir = cache_dir / "empty"
    cached = False
    if mount_info is None or mount_info.name != build_hash:
        volume_dir = overlay_dir / "volume"
        if mount_info is None:
            if not overlay_dir.is_dir():
                lower_dirs = [empty_dir]
                empty_dir.mkdir(parents=True, exist_ok=True)
                volume_dir.mkdir(parents=True, exist_ok=True)
                work_dir.mkdir(parents=True, exist_ok=True)
            else:
                lower_dirs = get_lower_dirs(overlay_dir, [empty_dir])
                cached = True
        else:
            fuseoverlayfs.unmount(build_dir)
            if not overlay_dir.is_dir():
                volume_dir.mkdir(parents=True, exist_ok=True)
                lower_dirs = get_lower_dirs(mount_info)
                lower_dirs.append(mount_info / "volume")
                save_lower_dirs(overlay_dir, lower_dirs)
            else:
                lower_dirs = get_lower_dirs(overlay_dir, [empty_dir])
                cached = True
        build_dir.mkdir(parents=True, exist_ok=True)
        fuseoverlayfs.mount(build_dir, lower_dirs, workdir=work_dir, upperdir=volume_dir)
    return cached
