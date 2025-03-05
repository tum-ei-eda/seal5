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
"""Patch utils for seal5."""
import os
import argparse
from pathlib import Path
from typing import Optional

from email.utils import formatdate
import yaml

from seal5 import utils
from seal5.logging import get_logger

logger = get_logger()


def generate_patch(index_file, llvm_dir=None, out_file=None, author=None, mail=None, msg=None, append=None):
    """Generate patch contents based on index file."""
    del append  # unused
    # base_dir = os.path.dirname(index_file)
    if msg:
        if not isinstance(msg, str):
            assert isinstance(msg, list)
            assert len(msg) == 1
            msg = msg[0]
    else:
        msg = "Placeholder"

    with open(index_file, "r", encoding="utf-8") as file:
        index = yaml.safe_load(file)

    global_artifacts = index["artifacts"]

    def generate_patch_set(fragments):
        ps = ""
        # Build minimal patch header for 'git am'
        user_name = author
        user_email = mail
        ps += f"From: {user_name} <{user_email}>\n"
        ps += f"Date: {formatdate()}\n"
        ps += f"Subject: {msg}\n\n\n"
        for fragment in fragments:
            ps += fragment
        return ps

    def find_site(path, key):
        # print("find_site", path, key)
        # start_mark = key + ' - INSERTION_START'
        # enc_mark = key + ' - INSERTION_END'
        if key:
            start_mark_ = path.split("/")[-1] + " - " + key + " - INSERTION_START"
            end_mark_ = path.split("/")[-1] + " - " + key + " - INSERTION_END"
        else:
            start_mark_ = path.split("/")[-1] + " - INSERTION_START"
            end_mark_ = path.split("/")[-1] + " - INSERTION_END"
        # print("start", start_mark_)
        # print("end", end_mark_)
        site_line = -1
        site_len = 0
        start_mark = None
        fullpath = path if llvm_dir is None else os.path.join(llvm_dir, path)
        with open(fullpath, "r", encoding="utf-8") as src:
            lines = src.readlines()
            for line in lines:
                if line.find(start_mark_) != -1:
                    start_mark = line
                    site_line = lines.index(line)
                elif line.find(end_mark_) != -1:
                    end_mark = line.rstrip("\n")
                    site_len = lines.index(line) - site_line + 1
                    break
                elif site_line >= 0:
                    # Accumulate all lines between the start mark and the end
                    # as part of the mark, so the new lines get injected just
                    # before the end mark
                    start_mark += line
        if start_mark is None:
            # fallback
            logger.warning("Marker not found: {path}, {key}. Retrying without key...")
            if key:
                return find_site(path, None)
            assert False, f"Marker not found: {path}, {key}"
        return site_line, site_len, start_mark, end_mark

    def generate_patch_fragment(artifact):
        dest_path = artifact.get("dest_path", None)
        src_path = artifact.get("src_path", None)
        key = artifact.get("key", None)
        start = artifact.get("start", None)
        end = artifact.get("end", None)
        line = artifact.get("line", None)
        content_ = artifact.get("content", None)
        assert dest_path is not None
        is_file = False
        is_dir = False
        is_patch = False
        # TODO: do not depend on dest_path
        if key:  # NamedPatch
            is_patch = True
        elif start is not None and end is not None:
            raise NotImplementedError
        elif line is not None:
            raise NotImplementedError
        else:  # File/Dir
            if content_ is None:
                if Path(src_path).is_file():
                    is_file = True
                elif Path(src_path).is_dir():
                    is_dir = True
                else:
                    raise RuntimeError(f"File not found: {src_path}")
            else:
                is_file = True
        if content_:
            assert isinstance(content_, str)
        else:
            if is_patch or is_file:
                with open(src_path, "r", encoding="utf-8") as f:
                    content_ = f.read()
            elif is_dir:
                files = Path(src_path).rglob("*")
                base = dest_path
                # print("base", base)
                # print("files", files)
                fragments = []
                for file in files:
                    if file.is_dir():
                        continue
                    # print("file", file)
                    dest_path_ = str(Path(base) / (str(file).replace(f"{src_path}/", "")))
                    # print("dest_path_", dest_path_)
                    src_path_ = file
                    file_artifact = {
                        "dest_path": str(dest_path_),
                        "src_path": str(src_path_),
                    }
                    fragment = generate_patch_fragment(file_artifact)
                    fragments.append(fragment)
                # print("fragments", fragments)
                # input("AAA")
                return "".join(fragments)
                # raise NotImplementedError
            else:
                assert False
        content = "+" + content_.replace("\n", "\n+")
        if is_patch:
            # Updating existing file
            orig_file = "a/" + dest_path
            new_file = "b/" + dest_path
            site_line, site_len, start_mark, end_mark = find_site(dest_path, key)
            new_start = site_line + 1
            new_len = content_.count("\n") + 1 + site_len
            # ensure all existing lines in the match prefixed by a space
            # if site_len > 2 and start_mark[-1] == "\n":
            # if False:
            #     start_mark = start_mark.rstrip("\n").replace("\n", "\n ")
            # else:
            start_mark = start_mark.rstrip("\n").replace("\n", "\n ")
            content = f" {start_mark}\n{content}\n {end_mark}"
        else:
            assert is_file
            # Adding new file
            orig_file = "/dev/null"
            new_file = "b/" + dest_path
            new_start = 1
            site_len = 0
            site_line = -1
            new_len = content_.count("\n") + 1
        return f"""--- {orig_file}
+++ {new_file}
@@ -{site_line + 1},{site_len} +{new_start},{new_len} @@
{content}
"""

    fragments = []

    def process_artifacts(artifacts):
        ret = []
        for artifact in artifacts:
            fragment = generate_patch_fragment(artifact)
            ret.append(fragment)
        return ret

    fragments.extend(process_artifacts(global_artifacts))

    for extn in index["extensions"]:
        fragments.extend(process_artifacts(extn["artifacts"]))

    patch_set = generate_patch_set(fragments)

    if out_file:
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(patch_set)
    else:
        print(patch_set)


def process_arguments():
    """Progress cmdline arguments."""
    parser = argparse.ArgumentParser(description="Generate patch file for adding extension to LLVM")
    parser.add_argument("index_file", help="list of code fragments to inject")
    parser.add_argument("--llvm-dir", type=str, default=None, help="path to llvm repo (default: cwd)")
    parser.add_argument("--out-file", type=str, default=None, help="write patchset to file (default: print to stdout)")
    parser.add_argument("--author", type=str, default="bob", help="author name in patchset")
    parser.add_argument("--mail", type=str, default="bob@bob.com", help="author mail in patchset")
    parser.add_argument(
        "--msg", type=str, nargs="+", default="[PATCH] Instructions injected", help="custom text for commit message"
    )
    parser.add_argument(
        "--append",
        "-a",
        action="store_true",
        help="whether existing patches should be appended instead of beeing overwritten",
    )
    args = parser.parse_args()
    return args


def analyze_diff(repo, base: str, cur: Optional[str] = None):
    args = ["git", "diff", "--shortstat"]
    args += [base]
    if cur is not None:
        args += [cur]
    out = utils.exec_getout(
        *args,
        cwd=repo.working_tree_dir,
        print_func=lambda *args, **kwargs: None,
        live=False,
    )
    n_files_changed = 0
    n_insertions = 0
    n_deletions = 0
    for x in out.split(","):
        x = x.strip()
        if len(x) == 0:
            continue
        val, key = x.split(" ", 1)
        val = int(val)
        if "files changed" in key or "file changed" in key:
            n_files_changed = val
        elif "insertions" in key:
            n_insertions = val
        elif "deletions" in key:
            n_deletions = val
    return n_files_changed, n_insertions, n_deletions


def main():
    """Main entry point."""
    args = process_arguments()
    generate_patch(
        args.index_file,
        llvm_dir=args.llvm_dir,
        out_file=args.out_file,
        author=args.authot,
        mail=args.mail,
        msg=args.msg,
        append=args.append,
    )


if __name__ == "__main__":
    main()
