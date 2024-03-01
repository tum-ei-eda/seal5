# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Very crude expression evaluation functions for use during model generation."""

from m2isar.metamodel import arch, behav


def group(self: behav.Group, context):
    return self.expr.generate(context)


def int_literal(self: behav.IntLiteral, context):
    return self.value


def named_reference(self: behav.NamedReference, context):
    if isinstance(self.reference, arch.Constant) and self.reference.value is not None:
        return self.reference.value
    return None
    # raise M2ValueError("non-interpretable value encountered")


def indexed_reference(self: behav.IndexedReference, context):
    idx = self.index.generate(context)
    return self.reference._initval[idx]


def binary_operation(self: behav.BinaryOperation, context):
    left = self.left.generate(context)
    right = self.right.generate(context)
    if left is None or right is None:
        return None
    return int(eval(f"{left}{self.op.value}{right}"))


def unary_operation(self: behav.UnaryOperation, context):
    right = self.right.generate(context)
    return int(eval(f"{self.op.value}{right}"))
