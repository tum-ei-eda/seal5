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

"""Git utils for seal5."""
from git import Actor

from seal5.settings import GitSettings


def get_author_from_settings(git_settings: GitSettings):
    if git_settings is None:
        author = "Unknown"
        mail = "unknown@example.com"
    else:
        author = git_settings.author
        mail = git_settings.mail
    return Actor(author, mail)
