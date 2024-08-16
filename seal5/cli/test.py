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
"""Command line subcommand for Testing seal5 environment."""

from seal5.flow import Seal5Flow
from seal5.logging import get_logger
from os import getenv


logger = get_logger()


def add_test_options(parser):
    test_parser = parser.add_argument_group("test options")
    test_parser.add_argument(
        "--debug",
        default=False,
        action="store_true",
        help="Debug?",
    )
    test_parser.add_argument(
        "--ignore-error",
        default=False,
        action="store_true",
        help="Ignore failed tests?",
    )
    test_parser.add_argument(
        "--config",
        nargs="?",
        type=str,
        default=None,
        help="LLVM test config",
    )


def get_parser(subparsers):
    """ "Define and return a subparser for the test subcommand."""
    parser = subparsers.add_parser("test", description="test Seal5 settings.")
    parser.set_defaults(func=handle)
    add_test_options(parser)
    return parser


def handle(args):
    """Callback function which will be called to process the test subcommand"""
    if args.dir is None:
        home_dir = getenv("SEAL5_HOME")
        if home_dir is not None:
            args.dir = home_dir
        else:
            logger.error("Seal5_HOME Env var not specified !!!")
    seal5_flow = Seal5Flow(args.dir, name=args.name)
    seal5_flow.test(
        debug=args.debug,
        verbose=args.verbose,
        ignore_error=args.ignore_error,
        config=args.config,
    )
