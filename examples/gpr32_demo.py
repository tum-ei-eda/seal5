#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Compatibility entry point for the RV32 register-pair example."""
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).with_name("regpairs_demo.py")), run_name="__main__")
