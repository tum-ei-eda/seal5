#!/usr/bin/env python
#
# Copyright (c) 2022 TUM Department of Electrical and Computer Engineering.
#
# This file is part of MLonMCU.
# See https://github.com/tum-ei-eda/mlonmcu.git for further info.
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

"""The setup script."""

import os
from setuptools import setup, find_packages
from seal5.version import __version__


def resource_files(directory):
    paths = []
    for path, directories, filenames in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join("..", path, filename))
    return paths


with open("README.md") as readme_file:
    readme = readme_file.read()


def get_requirements():
    return []


requirements = get_requirements()

setup(
    author="TUM Department of Electrical and Computer Engineering - Chair of Electronic Design Automation",
    author_email="philipp.van-kempen@tum.de",
    python_requires=">=3.8",
    classifiers=[  # TODO
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    description="Seal5 Project",
    entry_points={
        "console_scripts": [
            "seal5=seal5.cli.main:main",
        ],
    },
    install_requires=requirements,
    extras_require={},
    license="Apache License 2.0",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="seal5",
    name="seal5",
    packages=find_packages(include=["seal5", "seal5.*"]),
    package_data={"seal5": resource_files("resources")},
    test_suite="tests",
    tests_require=requirements,
    url="https://github.com/tum-ei-eda/seal5",
    version=__version__,
    zip_safe=False,
)
