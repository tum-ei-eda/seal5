# -*- Python -*-

# Configuration file for the 'lit' test runner.

import os
import sys
import re
import platform
import subprocess

import lit.util
import lit.formats
from lit.llvm import llvm_config
from lit.llvm.subst import FindTool
from lit.llvm.subst import ToolSubst

# name: The name of this test suite.
config.name = 'LLVM'

# testFormat: The test format to use to interpret tests.
# config.test_format = lit.formats.ShTest(not llvm_config.use_lit_shell)
config.test_format = lit.formats.ShTest(True)

# # suffixes: A list of file extensions to treat as test files. This is overriden
# # by individual lit.local.cfg files in the test subdirectories.
config.suffixes = ['.ll', '.c', '.test', '.txt', '.s', '.mir', '.yaml']
