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
"""Console script for seal5."""

import argparse
import sys


from seal5.logging import get_logger
from seal5.cli import init, load, setup, reset, clean, patch, build, install, transform, generate, test, deploy, export
from .common import handle_logging_flags, add_common_options
from ..version import __version__

logger = get_logger()


def main(args=None):
    """Console script for seal5."""
    parser = argparse.ArgumentParser(
        description="Seal5 Flow",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-V", "--version", action="version", version="mlonmcu " + __version__)
    add_common_options(parser)
    subparsers = parser.add_subparsers(dest="subcommand")  # this line changed
    init.get_parser(subparsers)
    load.get_parser(subparsers)
    setup.get_parser(subparsers)
    transform.get_parser(subparsers)
    reset.get_parser(subparsers)
    clean.get_parser(subparsers)
    patch.get_parser(subparsers)
    build.get_parser(subparsers)
    install.get_parser(subparsers)
    generate.get_parser(subparsers)
    test.get_parser(subparsers)
    deploy.get_parser(subparsers)
    export.get_parser(subparsers)
    if args:
        args = parser.parse_args(args)
    else:
        args = parser.parse_args()
    handle_logging_flags(args)

    if hasattr(args, "func"):
        args.func(args)
    else:
        print("Invalid subcommand for `seal5`!")
        parser.print_help(sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main(args=sys.argv[1:]))  # pragma: no cover
