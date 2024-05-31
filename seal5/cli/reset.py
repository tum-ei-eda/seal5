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
"""Command line subcommand for resetting the seal5 environment."""

from seal5.flow import Seal5Flow


def add_reset_options(parser):
    reset_parser = parser.add_argument_group("reset options")
    reset_parser.add_argument(
        "-n",
        "--name",
        metavar="NAME",
        nargs=1,
        type=str,
        default="default",
        help="Environment name (default: %(default)s)",
    )
    reset_parser.add_argument(
        "DIR",
        nargs="?",
        type=str,
        default="/home/hansos/temp/",
        help="LLVM directory (default: %(default)s",
    )
    reset_parser.add_argument(
        "--non-interactive",
        dest="non_interactive",
        default=True,
        action="store_true",
        help="Do not ask questions interactively",
    )

    reset_parser.add_argument(
        "--settings",
        default=False,
        dest="settings",
        action="store_true",
        help="Should settings be reset?",
    )
    reset_parser.add_argument(
        "--verbose",
        default=False,
        action="store_true",
        help="Verbose printing of steps into console",
    )


def get_parser(subparsers):
    """ "Define and return a subparser for the reset subcommand."""
    parser = subparsers.add_parser("reset", description="Reset Seal5 settings.")
    parser.set_defaults(func=handle)
    add_reset_options(parser)
    return parser


def handle(args):
    """Callback function which will be called to process the reset subcommand"""
    name = args.name[0] if isinstance(args.name, list) else args.name
    seal5_flow = Seal5Flow(args.DIR, name)
    seal5_flow.reset(settings=args.settings, verbose=args.verbose, interactive=not args.non_interactive)