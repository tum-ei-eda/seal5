# SPDX-License-Identifier: Apache-2.0
"""Seal5 extensions to the upstream CoreDSL behavior writer."""

from functools import singledispatchmethod

from m2isar.backends.coredsl2.visitor import CDSLWriterVisitor
from m2isar.metamodel import behav

from seal5.transform.normalize_subscripts import IndexedPartSelect
from seal5.transform.detect_branches import BranchIntrinsic


class Seal5CDSLWriterVisitor(CDSLWriterVisitor):
    @singledispatchmethod
    def generate(self, expr, writer):
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
