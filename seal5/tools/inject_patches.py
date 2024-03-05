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
import yaml
from pathlib import Path
from email.utils import formatdate

from seal5.logging import get_logger

logger = get_logger()


def generate_patch(index_file, llvm_dir=None, out_file=None, author=None, mail=None, msg=None, append=None):
    # base_dir = os.path.dirname(index_file)
    if msg:
        if not isinstance(msg, str):
            assert isinstance(msg, list)
            assert len(msg) == 1
            msg = msg[0]
    else:
        msg = "Placeholder"

    with open(index_file) as file:
        index = yaml.safe_load(file)

    global_artifacts = index["artifacts"]

    def generate_patch_set(fragments):
        ps = ""
        # Build minimal patch header for 'git am'
        userName = author
        userEmail = mail
        ps += "From: {0} <{1}>\n".format(userName, userEmail)
        ps += "Date: {0}\n".format(formatdate())
        ps += "Subject: {0}\n\n\n".format(msg)
        for fragment in fragments:
            ps += fragment
        return ps

    def find_site(path, key):
        # print("find_site", path, key)
        # startMark = key + ' - INSERTION_START'
        # endMark = key + ' - INSERTION_END'
        if key:
            startMark_ = path.split("/")[-1] + " - " + key + " - INSERTION_START"
            endMark_ = path.split("/")[-1] + " - " + key + " - INSERTION_END"
        else:
            startMark_ = path.split("/")[-1] + " - INSERTION_START"
            endMark_ = path.split("/")[-1] + " - INSERTION_END"
        # print("start", startMark_)
        # print("end", endMark_)
        siteLine = -1
        siteLen = 0
        startMark = None
        fullpath = path if llvm_dir is None else os.path.join(llvm_dir, path)
        with open(fullpath, "r") as src:
            lines = src.readlines()
            for line in lines:
                if line.find(startMark_) != -1:
                    startMark = line
                    siteLine = lines.index(line)
                elif line.find(endMark_) != -1:
                    endMark = line.rstrip("\n")
                    siteLen = lines.index(line) - siteLine + 1
                    break
                elif siteLine >= 0:
                    # Accumulate all lines between the start mark and the end
                    # as part of the mark, so the new lines get injected just
                    # before the end mark
                    startMark += line
        if startMark is None:
            # fallback
            if key:
                return find_site(path, None)
            else:
                assert False, "Marker not found!"
        return siteLine, siteLen, startMark, endMark

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
                with open(src_path, "r") as f:
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
            origFile = "a/" + dest_path
            newFile = "b/" + dest_path
            siteLine, siteLen, startMark, endMark = find_site(dest_path, key)
            newStart = siteLine + 1
            newLen = content_.count("\n") + 1 + siteLen
            # ensure all existing lines in the match prefixed by a space
            # if siteLen > 2 and startMark[-1] == "\n":
            if False:
                startMark = startMark.rstrip("\n").replace("\n", "\n ")
            else:
                startMark = startMark.rstrip("\n").replace("\n", "\n ")
            content = " {0}\n{1}\n {2}".format(startMark, content, endMark)
        else:
            assert is_file
            # Adding new file
            origFile = "/dev/null"
            newFile = "b/" + dest_path
            newStart = 1
            siteLen = 0
            siteLine = -1
            newLen = content_.count("\n") + 1
        return """--- {0}
+++ {1}
@@ -{2},{3} +{4},{5} @@
{6}
""".format(
            origFile, newFile, siteLine + 1, siteLen, newStart, newLen, content
        )

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
        with open(out_file, "w") as f:
            f.write(patch_set)
    else:
        print(patch_set)


def process_arguments():
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


def main():
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
