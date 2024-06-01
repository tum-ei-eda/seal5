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
"""Command line subcommand for Installing Seal5 dependencies"""

from seal5.flow import Seal5Flow


def add_setup_options(parser):
    setup_parser = parser.add_argument_group("setup options")
    setup_parser.add_argument(
        "-n",
        "--name",
        metavar="NAME",
        nargs=1,
        type=str,
        default="default",
        help="Environment name (default: %(default)s)",
    )
    setup_parser.add_argument(
        "-dir",
        nargs="?",
        type=str,
        default="~/.config/seal5/demo/",
        help="LLVM directory (default: %(default)s",
    )
    setup_parser.add_argument(
        "--non-interactive",
        default=False,
        dest="non_interactive",
        action="store_true",
        help="Do not ask questions interactively",
    )
    setup_parser.add_argument(
        "--verbose",
        default=False,
        action="store_true",
        help="Verbose printing of steps into console",
    )
    setup_parser.add_argument("--force", "-f", default=False, action="store_true", help="Overwrite Seal5 deps")


def get_parser(subparsers):
    """ "Define and return a subparser for the setup subcommand."""
    parser = subparsers.add_parser("setup", description="Setup Seal5 deps.")
    parser.set_defaults(func=handle)
    add_setup_options(parser)
    return parser


def handle(args):
    """Callback function which will be called to process the setup subcommand"""
    name = args.name[0] if isinstance(args.name, list) else args.name
    seal5_flow = Seal5Flow(args.DIR, name)
    seal5_flow.setup(
        interactive=not args.non_interactive,
        force=args.force,
        verbose=args.verbose,
    )
