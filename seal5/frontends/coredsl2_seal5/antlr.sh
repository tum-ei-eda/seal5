#!/bin/bash

# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

java -jar ../../../ext/antlr-4.12.0-complete.jar -o parser_gen -listener -visitor -Dlanguage=Python3 CoreDSL2.g4
