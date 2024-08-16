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
"""Command line subcommand for transforming Seal5 inputs .
    Transform inputs
      1. Create M2-ISA-R metamodel
      2. Convert to Seal5 metamodel (including aliases, builtins,...)
      3. Analyse/optimize instructions
"""

from seal5.flow import Seal5Flow
from seal5.logging import get_logger
from os import getenv


logger = get_logger()


def add_transform_options(parser):
    transform_parser = parser.add_argument_group("transform options")
    transform_parser.add_argument(
        "--skip",
        nargs="+",
        type=str,
        default=None,
        help="Passes that should be skipped",
    )
    transform_parser.add_argument(
        "--only",
        nargs="+",
        type=str,
        default=None,
        help="Passes that should be carried out",
    )


def get_parser(subparsers):
    """ "Define and return a subparser for the transform subcommand."""
    parser = subparsers.add_parser("transform", description="transform Seal5 models.")
    parser.set_defaults(func=handle)
    add_transform_options(parser)
    return parser


def handle(args):
    """Callback function which will be called to process the transform subcommand"""
    if args.dir is None:
        home_dir = getenv("SEAL5_HOME")
        if home_dir is not None:
            args.dir = home_dir
        else:
            logger.error("Seal5_HOME Env var not specified !!!")
    seal5_flow = Seal5Flow(args.dir, name=args.name)
    seal5_flow.transform(
        verbose=args.verbose,
        skip=None if args.skip is None else list(args.skip),
        only=None if args.only is None else list(args.only),
    )
