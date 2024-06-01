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
"""Command line subcommand for Exporting Seal5 artifacts"""

from seal5.flow import Seal5Flow


def add_export_options(parser):
    export_parser = parser.add_argument_group("export options")
    export_parser.add_argument(
        "-n",
        "--name",
        metavar="NAME",
        nargs=1,
        type=str,
        default="default",
        help="Environment name (default: %(default)s)",
    )
    export_parser.add_argument(
        "DIR",
        nargs="?",
        type=str,
        default="~/.config/seal5/demo/",
        help="LLVM directory (default: %(default)s",
    )
    export_parser.add_argument(
        "--dest",
        nargs="?",
        type=str,
        default="~/.config/seal5/demo/seal5artifact.tar.gz",
        help="Path to which compressed artifacts should go",
    )
    export_parser.add_argument(
        "--verbose",
        default=False,
        action="store_true",
        help="Verbose printing of steps into console",
    )


def get_parser(subparsers):
    """ "Define and return a subparser for the export subcommand."""
    parser = subparsers.add_parser("export", description="Export Seal5 artifacts.")
    parser.set_defaults(func=handle)
    add_export_options(parser)
    return parser


def handle(args):
    """Callback function which will be called to process the export subcommand"""
    name = args.name[0] if isinstance(args.name, list) else args.name
    seal5_flow = Seal5Flow(args.DIR, name)
    seal5_flow.export(dest=args.dest, verbose=args.verbose)
