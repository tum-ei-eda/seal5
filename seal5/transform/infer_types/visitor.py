# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Type inference for M2-ISA-R/Seal5 metamodel.

This module re-exports the upstream M2-ISA-R InferTypesMutator which provides
the modern visitor pattern and correct type system for type inference.
"""

# Re-export the InferTypesMutator from m2isar.transforms.infer_types
from m2isar.transforms.infer_types.visitor import InferTypesMutator
from m2isar.warnings import WarningsManager

__all__ = ["InferTypesMutator", "WarningsManager"]
