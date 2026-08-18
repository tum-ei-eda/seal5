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


# Minimal context stub for compatibility with emit_warning calls
class MinimalContext:
    """Minimal context for type inference compatible with seal5 usage."""
    def emit_warning(self, message, warning_id, logger=None, line_info=None):
        """Emit a warning (delegates to logger if provided)."""
        if logger:
            logger.warning(message)


# Re-export the InferTypesMutator from m2isar.transforms.infer_types
from m2isar.transforms.infer_types.visitor import InferTypesMutator

__all__ = ["InferTypesMutator", "MinimalContext"]
