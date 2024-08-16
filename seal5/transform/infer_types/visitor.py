# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""A transformation module for simplifying M2-ISA-R behavior expressions. The following
simplifications are done:

* Resolvable :class:`m2isar.metamodel.arch.Constant` s are replaced by
  `m2isar.metamodel.arch.IntLiteral` s representing their value
* Fully resolvable arithmetic operations are carried out and their results
  represented as a matching :class:`m2isar.metamodel.arch.IntLiteral`
* Conditions and loops with fully resolvable conditions are either discarded entirely
  or transformed into code blocks without any conditions
* Ternaries with fully resolvable conditions are transformed into only the matching part
* Type conversions of :class:`m2isar.metamodel.arch.IntLiteral` s apply the desired
  type directly to the :class:`IntLiteral` and discard the type conversion
"""
import logging
from copy import copy

from m2isar.metamodel import arch, behav

logger = logging.getLogger(__name__)

# pylint: disable=unused-argument


def operation(self: behav.Operation, context):
    statements = []
    for stmt in self.statements:
        # try:
        temp = stmt.generate(context)
        if isinstance(temp, list):
            statements.extend(temp)
        else:
            statements.append(temp)
        # except (NotImplementedError, ValueError):
        #   print(f"cant simplify {stmt}")

    self.statements = statements
    return self


def binary_operation(self: behav.BinaryOperation, context):
    # print("binary_operation")
    # print("self.op.value", self.op.value)

    self.left = self.left.generate(context)
    self.right = self.right.generate(context)
    # print("self.left", self.left)
    # print("self.right", self.right)

    # print("self.left.inferred_type", self.left.inferred_type)
    # print("self.right.inferred_type", self.right.inferred_type)

    # see: https://github.com/Minres/CoreDSL/wiki/Expressions#arithmetic-type-rules
    if self.op.value in ["+", "-", "*", "/", "%", "|", "&", "^", "<<", ">>"]:
        if self.left.inferred_type is None or self.right.inferred_type is None:
            logger.warning("Slice Operation needs inferred type. Skipping...")
            self.inferred_type = None
            return self
        assert isinstance(self.left.inferred_type, arch.IntegerType)
        assert isinstance(self.right.inferred_type, arch.IntegerType)
        w1 = self.left.inferred_type._width
        w2 = self.right.inferred_type._width
        s1 = self.left.inferred_type.signed
        s2 = self.right.inferred_type.signed
        if self.op.value == "+":
            if not s1 and not s2:
                wr = max(w1, w2) + 1
                sr = False
            elif s1 and s2:
                wr = max(w1, w2) + 1
                sr = True
            elif s1 and not s2:
                wr = max(w1, w2 + 1) + 1
                sr = True
            elif not s1 and s2:
                wr = max(w1 + 1, w2) + 1
                sr = True
        elif self.op.value == "-":
            sr = True
            if not s1 and not s2:
                wr = max(w1 + 1, w2 + 1)
            elif s1 and s2:
                wr = max(w1 + 1, w2 + 1)
            elif s1 and not s2:
                wr = max(w1, w2 + 1) + 1
            elif not s1 and s2:
                wr = max(w1 + 1, w2) + 1
        elif self.op.value == "*":
            wr = w1 + w2
            sr = s1 or s2
        elif self.op.value == "/":
            wr = w1 if not s2 else (w1 + 1)
            sr = s1 or s2
        elif self.op.value == "%":
            if not s1 and not s2:
                wr = min(w1, w2)
                sr = False
            elif s1 and s2:
                wr = min(w1, w2)
                sr = True
            elif s1 and not s2:
                wr = min(w1, w2 + 1)
                sr = True
            elif not s1 and s2:
                wr = min(w1, max(1, w2 - 1))
                sr = False
        elif self.op.value in ["|", "&", "^"]:
            wr = max(w1, w2)
            sr = s1 or s2
        elif self.op.value in [">>", "<<"]:
            wr = w1
            sr = s1
        self.inferred_type = arch.IntegerType(wr, sr, None)
    else:
        if self.op.value in ["||", "&&"]:
            self.inferred_type = arch.IntegerType(1, False, None)  # unsigned<1> / bool
        elif self.op.value in ["<", ">", "==", "!=", ">=", "<="]:
            self.inferred_type = arch.IntegerType(1, False, None)  # unsigned<1> / bool
    # print("sit", self.inferred_type.width)
    assert self.inferred_type is not None
    # input("!x!")

    return self


def slice_operation(self: behav.SliceOperation, context):
    # print("slice_operation")
    self.expr = self.expr.generate(context)
    self.left = self.left.generate(context)
    self.right = self.right.generate(context)
    # print("self.expr", self.expr)
    # print("self.left", self.left)
    # print("self.right", self.right)
    # input("slice")

    # type inference
    if self.expr.inferred_type is None:
        logger.warning("Slice Operation needs inferred type. Skipping...")
        return self
    assert isinstance(self.expr.inferred_type, arch.IntegerType)
    ty = self.expr.inferred_type
    # For non-static slices, we cann not infer the type!
    if not isinstance(self.left, behav.IntLiteral):
        logger.warning("Can not infer type of non-static slice operation. Skipping...")
        return self
    lval = self.left.value
    if not isinstance(self.right, behav.IntLiteral):
        logger.warning("Can not infer type of non-static slice operation. Skipping...")
        return self
    rval = self.right.value
    width = lval - rval + 1 if lval > rval else rval - lval + 1
    ty_ = copy(ty)
    ty_._width = width
    self.inferred_type = ty_
    # print("sit", ty)
    # input("*")

    return self


def concat_operation(self: behav.ConcatOperation, context):
    # print("concat_coperation")
    self.left = self.left.generate(context)
    self.right = self.right.generate(context)

    return self


def number_literal(self: behav.IntLiteral, context):
    # print("number_literal")
    if isinstance(self, behav.IntLiteral):
        bit_size = self.bit_size
        signed = self.signed

        self.inferred_type = arch.IntegerType(bit_size, signed, None)
    return self


def int_literal(self: behav.IntLiteral, context):
    # print("int_literal")

    # type inference
    bit_size = self.bit_size
    signed = self.signed

    self.inferred_type = arch.IntegerType(bit_size, signed, None)

    return self


def scalar_definition(self: behav.ScalarDefinition, context):
    # type inference
    # print("scalar_definition", self, dir(self), self.scalar, self.scalar.size, self.scalar.data_type)
    signed = self.scalar.data_type == arch.DataType.S
    width = self.scalar.size
    self.inferred_type = arch.IntegerType(width, signed, None)
    return self


def assignment(self: behav.Assignment, context):
    # print("assignment", self)
    # print("at_", self.target)
    # print("ae_", self.expr)
    self.target = self.target.generate(context)
    self.expr = self.expr.generate(context)

    # if isinstance(self.expr, behav.IntLiteral) and isinstance(self.target, behav.ScalarDefinition):
    #       self.target.scalar.value = self.expr.value

    # type inference
    # print("at", self.target)
    # print("ae", self.expr)
    # print("at1", self.target.inferred_type)
    # print("ae1", self.expr.inferred_type)
    # print("at2", self.target.inferred_type.width)
    # print("ae2", self.expr.inferred_type.width)
    # input("ccc")
    self.inferred_type = None

    return self


def conditional(self: behav.Conditional, context):
    self.conds = [x.generate(context) for x in self.conds]
    # self.stmts = [[y.generate(context) for y in x] for x in self.stmts]
    stmts = []
    for stmt in self.stmts:
        if isinstance(stmt, list):  # TODO: legacy?
            new = [y.generate(context) for y in stmt]
        else:
            new = stmt.generate(context)
        stmts.append(new)
    self.stmts = stmts

    return self


def loop(self: behav.Loop, context):
    self.cond = self.cond.generate(context)
    self.stmts = [x.generate(context) for x in self.stmts]

    return self


def ternary(self: behav.Ternary, context):
    # print("ternary")

    self.cond = self.cond.generate(context)
    self.then_expr = self.then_expr.generate(context)
    self.else_expr = self.else_expr.generate(context)

    # print("ste", self.then_expr)
    # print("see", self.else_expr)
    # print("ste1", self.then_expr.inferred_type)
    # print("see1", self.else_expr.inferred_type)
    # print("ste2", self.then_expr.inferred_type.width)
    # print("see2", self.else_expr.inferred_type.width)
    # TODO
    then_ty = self.then_expr.inferred_type
    else_ty = self.else_expr.inferred_type
    if then_ty and else_ty:
        # assert then_ty.signed == else_ty.signed
        wt = then_ty.width
        we = else_ty.width
        wr = max(wt, we)
        # print("wr", wr)
        # input("o")
        self.inferred_type = arch.IntegerType(wr, True, None)
    # input("ppp")

    return self


def return_(self: behav.Return, context):
    if self.expr is not None:
        self.expr = self.expr.generate(context)

    return self


def unary_operation(self: behav.UnaryOperation, context):
    # print("unary_operation")

    self.right = self.right.generate(context)

    # print("sr", self.right)
    # print("sr1", self.right.inferred_type)
    # print("sr2", self.right.inferred_type.width)
    # input("!")
    if self.right.inferred_type:
        w1 = self.right.inferred_type.width
        if self.op.value == "-":
            inferred_type = arch.IntegerType(w1 + 1, True, None)
        elif self.op.value == "~":
            inferred_type = arch.IntegerType(w1, True, None)
        elif self.op.value == "!":
            inferred_type = arch.IntegerType(1, False, None)
        else:
            inferred_type = None
        self.inferred_type = inferred_type

    return self


def named_reference(self: behav.NamedReference, context):
    # print("named_reference", self)
    # print("dir", dir(self))
    # print("self.reference", self.reference)
    reference = self.reference

    # type inference
    # self.infered_type = ?
    if isinstance(reference, arch.BitFieldDescr):
        # print("BITFIELD")
        # print("self.reference", self.reference)
        # print("self.reference.data_type", self.reference.data_type)
        assert self.reference.data_type in [arch.DataType.U, arch.DataType.S]
        ty = arch.IntegerType(reference.size, reference.data_type == arch.DataType.S, None)
        # print("ty", ty)
        self.inferred_type = ty

    elif isinstance(reference, arch.Scalar):
        dt = reference.data_type
        sz = reference.size
        assert dt in [arch.DataType.U, arch.DataType.S]
        signed = dt == arch.DataType.S
        ty = arch.IntegerType(sz, signed, None)
        self.inferred_type = ty
    elif isinstance(reference, arch.Memory):
        if reference.is_pc:  # TODO: check if special case required?
            self.inferred_type = arch.IntegerType(reference.size, False, None)
        # print("type(reference)", type(reference))

    # print("self.inferred_type", self.inferred_type)
    # input("222")

    return self


def indexed_reference(self: behav.IndexedReference, context):
    # print("indexed_reference")
    self.index = self.index.generate(context)

    # type inference
    assert isinstance(self.reference, arch.Memory)
    ty = arch.DataType.U  # TODO: Memory class should keep track of dtype, not only size?
    assert ty in [arch.DataType.U, arch.DataType.S]
    size = self.reference.size
    ty_ = arch.IntegerType(size, ty == arch.DataType.S, None)

    self.inferred_type = ty_
    # print("self.inferred_type", self.inferred_type)
    # input("111")

    return self


def type_conv(self: behav.TypeConv, context):
    # print("type_conv")
    self.expr = self.expr.generate(context)
    # print("self.expr", self.expr)

    ty = self.expr.inferred_type
    if ty is None:
        logger.warning("Type conv needs inferred type. Skipping...")
        return self
    assert isinstance(ty, arch.IntegerType)
    assert self.data_type in [arch.DataType.U, arch.DataType.S]
    ty.signed = self.data_type == arch.DataType.S
    if self.size is not None:
        ty._width = self.size

    # type inference
    self.inferred_type = ty

    return self


def callable_(self: behav.Callable, context):
    self.args = [stmt.generate(context) for stmt in self.args]

    return self


def procedure_call(self: behav.ProcedureCall, context):
    self.args = [stmt.generate(context) for stmt in self.args]

    return self


def group(self: behav.Group, context):
    self.expr = self.expr.generate(context)

    if isinstance(self.expr, behav.IntLiteral):
        return self.expr

    # type inference
    self.inferred_type = self.expr.inferred_type

    return self
