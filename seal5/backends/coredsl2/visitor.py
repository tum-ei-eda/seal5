# SPDX-License-Identifier: Apache-2.0
"""Seal5 extensions to the upstream CoreDSL behavior writer."""

from functools import singledispatchmethod

from m2isar.backends.coredsl2.visitor import CDSLWriterVisitor
from m2isar.metamodel import behav
from m2isar.metamodel.type_info import TypeKind

from seal5.transform.normalize_subscripts import IndexedPartSelect
from seal5.transform.detect_branches import BranchIntrinsic


class Seal5CDSLWriterVisitor(CDSLWriterVisitor):
    @singledispatchmethod
    def generate(self, expr, writer):
        return super().generate(expr, writer)

    @generate.register
    def _(self, expr: behav.BinaryOperation, writer):
        left = expr.left
        while isinstance(left, behav.Group):
            left = left.expr
        if (
            expr.op.value in ("<<", ">>")
            and isinstance(left, behav.Literal)
            and left.ty.kind in (TypeKind.INT, TypeKind.UINT)
            and left.ty.size is not None
        ):
            # Constant folding can replace an explicit cast with a typed literal.
            # Printing only its value loses the shift's data width (e.g. a
            # 32-bit one shifted by a 5-bit count becomes a 5-bit operation).
            signedness = "signed" if left.ty.kind == TypeKind.INT else "unsigned"
            writer.write(f"(({signedness}<{left.ty.size}>){left.value}) {expr.op.value} ")
            self.generate_grouped(expr.right, writer)
            return
        return super().generate(expr, writer)

    @generate.register
    def _(self, expr: BranchIntrinsic, writer):
        writer.write("branch(")
        self.generate(expr.args[0], writer)
        writer.write(")")

    @generate.register
    def _(self, expr: IndexedPartSelect, writer):
        self.generate(expr.expr, writer)
        writer.write("[")
        self.generate(expr.base, writer)
        writer.write(f" +: {expr.width}]")

    @generate.register
    def _(self, expr: behav.IndexedReference, writer):
        # The upstream writer currently drops the right bound altogether.
        writer.write(expr.reference.name)
        writer.write("[")
        self.generate(expr.index, writer)
        if expr.right is not None:
            writer.write(":")
            self.generate(expr.right, writer)
        writer.write("]")
