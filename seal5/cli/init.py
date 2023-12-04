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
"""Command line subcommand for initializing a seal5 environment."""

import os

from seal5.flow import Seal5Flow


def add_init_options(parser):
    init_parser = parser.add_argument_group("init options")
    init_parser.add_argument(
        "-n",
        "--name",
        metavar="NAME",
        nargs=1,
        type=str,
        default="default",
        help="Environment name (default: %(default)s)",
    )
    init_parser.add_argument(
        "DIR",
        nargs="?",
        type=str,
        default=".",
        help="LLVM directory (default: %(default)s",
    )
    init_parser.add_argument(
        "--non-interactive",
        dest="non_interactive",
        action="store_true",
        help="Do not ask questions interactively",
    )
    init_parser.add_argument(
        "--clone",
        default=None,
        action="store_true",
        help="Clone LLVM repository",
    )
    init_parser.add_argument(
        "--force",
        "-f",
        default=None,
        action="store_true",
        help="Allow overwriting an existing seal5 directory",
    )


def get_parser(subparsers):
    """ "Define and return a subparser for the init subcommand."""
    parser = subparsers.add_parser("init", description="Initialize Seal5.")
    parser.set_defaults(func=handle)
    add_init_options(parser)
    return parser


def handle(args):
    """Callback function which will be called to process the init subcommand"""
    name = args.name[0] if isinstance(args.name, list) else args.name
    seal5_flow = Seal5Flow(args.DIR, name)
    seal5_flow.initialize(
        interactive=not args.non_interactive,
        clone=args.clone,
        force=args.force,
    )
