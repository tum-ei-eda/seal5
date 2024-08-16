# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""TODO"""

from m2isar.metamodel import arch, behav

# pylint: disable=unused-argument

# import sys
# import traceback


def operation(self: behav.Operation, writer):
    # print("operation", self.statements)
    if len(self.statements) > 1:
        writer.enter_block()
    for stmt in self.statements:
        stmt.generate(writer)
        if not isinstance(stmt, (behav.Conditional, behav.Operation)):
            writer.write_line(";")
    if len(self.statements) > 1:
        writer.leave_block()


def binary_operation(self: behav.BinaryOperation, writer):
    writer.write("(")
    self.left.generate(writer)
    writer.write(f") {self.op.value} (")
    self.right.generate(writer)
    writer.write(")")


def slice_operation(self: behav.SliceOperation, writer):
    # print("slice_operation")
    self.expr.generate(writer)
    writer.write("[(")
    self.left.generate(writer)
    writer.write("):(")
    self.right.generate(writer)
    writer.write(")]")


def concat_operation(self: behav.ConcatOperation, writer):
    # print("concat_operation")
    # TODO: only add () where required
    writer.write("(")
    self.left.generate(writer)
    writer.write(") :: (")
    self.right.generate(writer)
    writer.write(")")


def number_literal(self: behav.IntLiteral, writer):
    # print("number_literal")
    writer.write(self.value)


def int_literal(self: behav.IntLiteral, writer):
    # print("int_literal")
    writer.write(self.value)


def scalar_definition(self: behav.ScalarDefinition, writer):
    # print("scalar_definition", self.scalar, dir(self.scalar))
    # input("u")
    writer.write_type(self.scalar.data_type, self.scalar.size)
    writer.write(" ")
    writer.write(self.scalar.name)
    if self.scalar.value:
        writer.write(" = ")
        writer.write(self.scalar.value)
    # writer.write_line(";")


def break_(self: behav.Break, writer):
    # print("break_")
    writer.write_line("break;")


def assignment(self: behav.Assignment, writer):
    # print("assignment", self, dir(self))
    # traceback.print_stack(file=sys.stdout)
    self.target.generate(writer)
    writer.write(" = ")
    self.expr.generate(writer)
    # print("writer.text", writer.text)
    # input("assign")
    # writer.write_line(";")
    # input("123")


def conditional(self: behav.Conditional, writer):
    # print("conditional")
    for i, stmt in enumerate(self.stmts):
        if i == 0:
            writer.write("if (")
            self.conds[i].generate(writer)
            writer.write(")")
        elif i > 0 and i < len(self.conds):
            writer.write("else if(")
            self.conds[i].generate(writer)
            writer.write(")")
        else:
            writer.write("else")
        writer.enter_block()
        # print("stmt", stmt)
        # input("ABC")
        stmt.generate(writer)
        if not isinstance(stmt, (behav.Conditional, behav.Operation)):
            writer.write_line(";")
        nl = len(self.stmts) > i
        writer.leave_block(nl=nl)


def loop(self: behav.Loop, writer):
    # print("loop")
    writer.write("while (")
    self.cond.generate(writer)
    writer.write(")")
    writer.enter_block()
    for stmt in self.stmts:
        stmt.generate(writer)
    writer.leave_block()


def ternary(self: behav.Ternary, writer):
    # print("ternary")
    writer.write("(")
    self.cond.generate(writer)
    writer.write(") ? (")
    self.then_expr.generate(writer)
    writer.write(") : (")
    self.else_expr.generate(writer)
    writer.write(")")


def return_(self: behav.Return, writer):
    # print("return_")
    writer.write("return")
    if self.expr is not None:
        writer.write(" ")
        self.expr.generate(writer)
    # writer.write_line(";")


def unary_operation(self: behav.UnaryOperation, writer):
    # print("unary_operation")
    writer.write(self.op.value)
    writer.write("(")
    self.right.generate(writer)
    writer.write(")")


def named_reference(self: behav.NamedReference, writer):
    # print("named_reference", self.reference.name)
    writer.write(self.reference.name)
    if isinstance(self.reference, (arch.Constant, arch.Memory, arch.Scalar)):
        # writer.track(self.reference.name)
        pass
    # if isinstance(self.reference, arch.Constant):
    # 	return behav.IntLiteral(self.reference.value, self.reference.size, self.reference.signed)

    # if isinstance(self.reference, arch.Scalar) and self.reference.value is not None:
    # 		return behav.IntLiteral(self.reference.value, self.reference.size, self.reference.data_type == arch.DataType.S)


def indexed_reference(self: behav.IndexedReference, writer):
    # print("indexed_reference", self.reference.name)
    writer.write(self.reference.name)
    writer.write("[")
    # if isinstance(self.reference, arch.Memory):
    #     # writer.track(self.reference.name)
    #     pass
    self.index.generate(writer)
    writer.write("]")


def type_conv(self: behav.TypeConv, writer):
    # print("type_conv", self, dir(self))
    writer.write("(")
    writer.write_type(self.data_type, self.size)
    writer.write(")")
    writer.write("(")
    self.expr.generate(writer)
    writer.write(")")


def callable_(self: behav.Callable, writer):
    # print("callable_", self, dir(self))
    # traceback.print_stack(file=sys.stdout)
    # input("55")
    # print("args", self.args)
    # print("ron", self.ref_or_name)
    # input("q")
    ref = self.ref_or_name
    if isinstance(ref, arch.Function):
        writer.write(ref.name)
    else:
        raise NotImplementedError
    writer.write("(")
    for i, stmt in enumerate(self.args):
        stmt.generate(writer)
        if i < len(self.args) - 1:
            writer.write(", ")
    writer.write(")")


def group(self: behav.Group, writer):
    # print("group")
    # writer.enter_block()
    writer.write("(")
    self.expr.generate(writer)
    writer.write(")")
    # writer.leave_block()
