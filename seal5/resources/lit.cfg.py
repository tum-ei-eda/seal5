# -*- Python -*-

# Configuration file for the 'lit' test runner.

import lit.util
import lit.formats
from lit.llvm import llvm_config

# name: The name of this test suite.
config.name = "LLVM"

# testFormat: The test format to use to interpret tests.
# config.test_format = lit.formats.ShTest(not llvm_config.use_lit_shell)
config.test_format = lit.formats.ShTest(True)

# # suffixes: A list of file extensions to treat as test files. This is overriden
# # by individual lit.local.cfg files in the test subdirectories.
config.suffixes = [".ll", ".c", ".test", ".txt", ".s", ".mir", ".yaml"]

import subprocess

# Query LLVM version
llvm_version = subprocess.check_output(["llvm-as", "--version"], text=True).split("version", 1)[1].split(" ")[1]
major_version = int(llvm_version.split(".")[0])

# Add a substitution for FileCheck
config.substitutions.append(("%llvm_major_version%", str(major_version)))
