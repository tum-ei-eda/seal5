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
import logging

from seal5.logging import get_logger, set_log_level

logger = get_logger()


def handle_logging_flags(args):
    # TODO: --log LEVEL
    if hasattr(args, "verbose") and hasattr(args, "quiet"):
        if args.verbose and args.quiet:
            raise RuntimeError("--verbose and --quiet can not be used at the same time")
        elif args.verbose:
            set_log_level(logging.DEBUG)
        elif args.quiet:
            set_log_level(logging.WARNING)
        else:
            set_log_level(logging.INFO)


def add_common_options(parser):
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print detailed messages for easier debugging (default: %(default)s)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Reduce number of logging statements to a minimum (default: %(default)s)",
    )
