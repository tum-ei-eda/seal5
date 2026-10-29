# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Type inference for M2-ISA-R/Seal5 metamodel.

Extend upstream inference for fixed-width ranges and preserve explicit cast kinds.
"""

from functools import singledispatchmethod

from m2isar.metamodel import arch, behav, type_info
from m2isar.transforms.infer_types.visitor import InferTypesMutator as UpstreamInferTypesMutator
from m2isar.warnings import WarningsManager

from seal5.transform.explicit_names import distance


class InferTypesMutator(UpstreamInferTypesMutator):
    @singledispatchmethod
    def generate(self, expr, context):
        return super().generate(expr, context)

    @generate.register
    def _(self, expr: behav.TypeConv, context):
        result = super().generate(expr, context)
        if result.ty is not None:
            # Modern PrimitiveType uses kind; assigning the legacy `signed`
            # member leaves the cast's actual type (and emitted CDSL) unchanged.
            result.ty.kind = expr.data_type
        return result

    @generate.register
    def _(self, expr: behav.IndexedReference, context):
        if expr.right is None or not isinstance(expr.reference.ty, type_info.ArrayType):
            return super().generate(expr, context)
        expr.index = self.generate(expr.index, context)
        expr.right = self.generate(expr.right, context)
        delta = distance(expr.index, expr.right)
        if delta is None:
            return super().generate(expr, context)
        element = expr.reference.ty.element_type
        expr.ty = type_info.PrimitiveType(element.kind, (abs(delta) + 1) * arch.get_const_or_val(element.size))
        return expr

__all__ = ["InferTypesMutator", "WarningsManager"]
