# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""TODO"""

from m2isar.metamodel import arch, behav
from seal5 import model

# pylint: disable=unused-argument


def operation(self: behav.Operation, context):
    statements = []
    for stmt in self.statements:
        temp = stmt.generate(context)
        if isinstance(temp, list):
            statements.extend(temp)
        else:
            statements.append(temp)

    self.statements = statements
    return self


def binary_operation(self: behav.BinaryOperation, context):
    self.left = self.left.generate(context)
    self.right = self.right.generate(context)

    return self


def slice_operation(self: behav.SliceOperation, context):
    self.expr = self.expr.generate(context)
    self.left = self.left.generate(context)
    self.right = self.right.generate(context)

    return self


def concat_operation(self: behav.ConcatOperation, context):
    self.left = self.left.generate(context)
    self.right = self.right.generate(context)

    return self


def number_literal(self: behav.IntLiteral, context):
    return self


def int_literal(self: behav.IntLiteral, context):
    return self


def scalar_definition(self: behav.ScalarDefinition, context):
    return self


def break_(self: behav.Break, context):
    return self


def assignment(self: behav.Assignment, context):
    self.target = self.target.generate(context)
    self.expr = self.expr.generate(context)

    return self


def conditional(self: behav.Conditional, context):
    # print("conditional")
    self.conds = [x.generate(context) for x in self.conds]
    self.stmts = [x.generate(context) for x in self.stmts]

    return self


def loop(self: behav.Loop, context):
    self.cond = self.cond.generate(context)
    self.stmts = [x.generate(context) for x in self.stmts]

    return self


def ternary(self: behav.Ternary, context):
    self.cond = self.cond.generate(context)
    self.then_expr = self.then_expr.generate(context)
    self.else_expr = self.else_expr.generate(context)

    return self


def return_(self: behav.Return, context):
    if self.expr is not None:
        self.expr = self.expr.generate(context)

    return self


def unary_operation(self: behav.UnaryOperation, context):
    self.right = self.right.generate(context)

    return self


def named_reference(self: behav.NamedReference, context):
    # if isinstance(self.reference, arch.BitFieldDescr):
    # raise NotImplementedError
    return self


def indexed_reference(self: behav.IndexedReference, context):
    print("indexed_reference", self)
    # print("self.reference", self.reference)
    # print("self.index", self.index)
    # print("self.index_", self.index)
    if isinstance(self.reference, arch.Memory):
        mem_name = self.reference.name
        mem = self.reference
        mem_size = mem.size
        mem_lanes = 1
        if mem_name == "MEM":
            return self
        index_left = self.index
        index_right = self.right
        offset = 0
        if isinstance(index_right, behav.BinaryOperation):  # offset?
            assert isinstance(index_left, behav.BinaryOperation)
            # TODO: check for eqivalent operation
            # print("binop!")
            if index_right.op.value == "+":
                # print("offset!")
                if isinstance(index_right.left, behav.NamedReference):
                    # print("lhs named")
                    if isinstance(index_right.right, behav.IntLiteral):
                        # print("rhs const")
                        offset = index_right.right.value
                        index_right = index_right.left
                        index_left = index_left.left
                elif isinstance(index_right.right, behav.NamedReference):
                    # print("rhs named")
                    if isinstance(index_right.left, behav.IntLiteral):
                        # print("lhs const")
                        offset = index_right.left.value
                        index_right = index_right.right
                        index_left = index_left.right
        # print("index_left", index_left)
        # print("index_right", index_right)
        # print("offset", offset)
        if isinstance(index_right, behav.NamedReference):
            # print("index_right -> named")
            if isinstance(index_right.reference, arch.BitFieldDescr):
                # print("index_right.reference -> bfd")
                op_name = index_right.reference.name
                if isinstance(index_left, behav.NamedReference):
                    # print("index_left -> named")
                    if isinstance(index_left.reference, arch.BitFieldDescr):
                        # print("index_left.reference -> bfd")
                        op_name_ = index_left.reference.name
                        assert op_name_ == op_name
                        assert op_name in context.operands
                        op = context.operands[op_name]
                        if mem_name == "X":
                            if offset == 0:
                                reg_class = model.Seal5RegisterClass.GPR
                            elif offset == 8:
                                reg_class = model.Seal5RegisterClass.GPRC
                            else:
                                # return self
                                raise NotImplementedError(f"GPR with offset {offset}")
                        elif mem_name == "F":
                            assert offset == 0
                            reg_class = model.Seal5RegisterClass.FPR
                        elif mem_name == "CSR":
                            assert offset == 0
                            reg_class = model.Seal5RegisterClass.CSR
                        else:
                            assert offset == 0  # TODO: write offset to Operand class?
                            reg_class = model.Seal5RegisterClass.UNKNOWN
                        if not isinstance(op, model.Seal5RegOperand):
                            op = model.Seal5RegOperand(op.name, op.ty, op.attributes, op.constraints, reg_class=reg_class)
                        reg_ty = model.Seal5Type(arch.DataType.U, mem_size, mem_lanes)
                        op.reg_ty = reg_ty
                        context.operands[op_name] = op
                elif isinstance(index_left, behav.BinaryOperation):
                    # print("index_left -> binop")
                    # only supporting X[rd+1:rd], NOT X[rd:rd+1] so far
                    op_name_ = index_left.left.reference.name
                    assert op_name_ == op_name
                    assert op_name in context.operands
                    op = context.operands[op_name]
                    if index_left.op.value == "+":
                        # print("op.value -> +")
                        offset = None
                        # print("il.l", index_left.left)
                        # print("il.r", index_left.right)
                        if isinstance(index_left.left, behav.NamedReference) and isinstance(index_left.left.reference, arch.BitFieldDescr):
                            # print("index_left.left -> bfr")
                            assert index_left.left.reference.name == op_name, "slice base register missmatch"
                            if isinstance(index_left.right, behav.IntLiteral):
                                offset = index_left.right.value
                        elif isinstance(index_left.right, behav.NamedReference) and isinstance(index_left.right.reference, arch.BitFieldDescr):
                            # print("index_left.right -> bfr")
                            assert index_left.right.reference.name == op_name, "slice base register missmatch"
                            if isinstance(index_left.left, behav.IntLiteral):
                                offset = index_left.left.value
                        else:
                            raise NotImplementedError
                        assert offset is not None
                        assert offset == 1, "only supporting gpr32pair"
                        assert mem_size == 32, "gprpair implies 32bit size"
                        assert mem_name == "X", "regpairs only supported for GPR memory named X"
                        reg_class = model.Seal5RegisterClass.GPR32Pair
                        # print("reg_class", reg_class)
                        # print("op", op)
                        if not isinstance(op, model.Seal5RegOperand):
                            # print("not is")
                            op = model.Seal5RegOperand(op.name, op.ty, op.attributes, op.constraints, reg_class=reg_class)
                        else:
                            pass
                            # print("skipping")  # TODO: check for conflicts
                        # print("op_", op)
                        # input("124")

                        mem_lanes = 1
                        mem_size_ = mem_size * 2
                        reg_ty = model.Seal5Type(arch.DataType.U, mem_size_, mem_lanes)
                        op.reg_ty = reg_ty
                        context.operands[op_name] = op
                    else:
                        raise NotImplementedError
                # input("1111")
    # input("1111")
    self.index = self.index.generate(context)

    return self


def type_conv(self: behav.TypeConv, context):
    self.expr = self.expr.generate(context)

    return self


def callable_(self: behav.Callable, context):
    self.args = [stmt.generate(context) for stmt in self.args]

    return self


def group(self: behav.Group, context):
    self.expr = self.expr.generate(context)

    return self


def procedure_call(self: behav.ProcedureCall, context):
    self.fn_args = [arg.generate(context) for arg in self.args]
    return self
