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
"""Command line subcommand for initializing Seal5 environment."""
from os import getenv

from seal5.flow import Seal5Flow
from seal5.logging import get_logger


logger = get_logger()


def add_init_options(parser):
    init_parser = parser.add_argument_group("init options")
    init_parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Do not ask questions interactively",
    )
    init_parser.add_argument(
        "--clone",
        "-c",
        action="store_true",
        help="Clone LLVM repository",
    )
    init_parser.add_argument(
        "--clone-url",
        default="https://github.com/llvm/llvm-project.git",
        help="Corresponding LLVM repository URL",
    )
    init_parser.add_argument(
        "--clone-ref",
        default="llvmorg-18.1.0-rc3",
        help="Corresponding LLVM repository commit/tag",
    )
    init_parser.add_argument(
        "--clone-depth",
        default=None,
        type=int,
        help="LLVM clone depth (use 1 for shallow clone)",
    )
    init_parser.add_argument(
        "--progress",
        action="store_true",
        help="Show progress bar during LLVM clone",
    )
    init_parser.add_argument(
        "--force",
        "-f",
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
    if args.dir is None:
        home_dir = getenv("SEAL5_HOME")
        if home_dir is not None:
            args.dir = home_dir
        else:
            logger.error("Seal5_HOME Env var not specified !!!")
    seal5_flow = Seal5Flow(args.dir, name=args.name)
    seal5_flow.initialize(
        interactive=not args.non_interactive,
        clone=args.clone,
        clone_url=args.clone_url,
        clone_ref=args.clone_ref,
        clone_depth=args.clone_depth if isinstance(args.clone_depth, int) and args.clone_depth > 0 else None,
        progress=args.progress,
        force=args.force,
        verbose=args.verbose,
    )
