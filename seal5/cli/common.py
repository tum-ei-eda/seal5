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
from seal5.logging import get_logger, set_log_level

logger = get_logger()


def handle_logging_flags(args):
    level = args.log.upper()
    set_log_level(level)


def add_common_options(parser):
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print tool outputs for easier debugging (default: %(default)s)",
    )
    parser.add_argument(
        "-n",
        "--name",
        metavar="NAME",
        type=str,
        default=None,
        help="Environment name",
    )
    parser.add_argument(
        "--dir",
        type=str,
        default=None,
        help="LLVM directory (default: %(default)s",
    )
