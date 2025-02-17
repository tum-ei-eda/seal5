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

from seal5.logging import get_logger
from seal5.wrapper import run_seal5_flow


logger = get_logger()


def add_wrapper_options(parser):
    """Setup parser for wrapper argument group."""
    wrapper_parser = parser.add_argument_group("wrapper options")
    wrapper_parser.add_argument(
        "files",
        nargs="*",
        help="Input files for seal5 flow",
    )
    wrapper_parser.add_argument(
        "--out-dir",
        type=str,
        default=None,
        help="Destination of artifacts",
    )


def get_parser(subparsers):
    """ "Define and return a subparser for the wrapper subcommand."""
    parser = subparsers.add_parser("wrapper", description="Run Seal5 Wrapper.")
    parser.set_defaults(func=handle)
    add_wrapper_options(parser)
    return parser


def handle(args):
    """Callback function which will be called to process the export subcommand"""
    run_seal5_flow(args.files, dest=args.dir, out_dir=args.out_dir)
