# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""TODO"""

# import tkinter as tk
import traceback

from m2isar import flatten
from m2isar.metamodel import arch, behav
from .context import DAGBuilderContext
from .dag import DAGAssignment, DAGOperand, DAGType, DAGUnary, DAGBinary, DAGTernary, DAGQuaternary, DAGImm
# from anytree import Node

# pylint: disable=unused-argument

LOOKUP = {
    "+": "add",
    "*": "mul",
    "-": "sub",
    "%": "srem/urem",
    "&": "and",
    "|": "or",
    "^": "xor",
    "<<": "shl",
    ">>": "srl",
    ">>>": "sra",
    "**": "pow",  # TODO
    "<": "setlt",
    ">": "setgt",
    "<=": "setle",
    ">=": "setge",
    "==": "seteq",
    "!=": "setne",
}

def operation(self: behav.Operation, context: "DAGBuilderContext"):
    # print("operation")

    patterns = {}  # destination : DAGOperation
    prev = None
    for i, stmt in enumerate(self.statements):
        try:
            ret, ret2 = stmt.generate(context)
        except Exception as e:
            print("Failed to build DAG")
            print(traceback.format_exc())
            ret = None
            ret2 = None
        # print("ret", ret)
        # print("ret2", ret2)  # DAGAssignment
        dest = f"pat{i}"
        expr = ret2
        if isinstance(ret2, DAGAssignment):
            # print("ret.target", type(ret.target))
            # print("ret2", ret2)
            if isinstance(ret.target, behav.NamedReference):
                dest = ret.target.reference.name
                expr = ret2.expr
            else:
                # TODO: handle simd behavior (lanes etc.) here
                # LHS slices are currently rewritten, so we need to skip those!
                expr = None
        if expr is None:
            continue
        patterns[dest] = expr

    # check for indexed stores
    for dest, expr in patterns.items():
        if isinstance(expr, DAGBinary):
            # print("expr", expr)
            if expr.name in ["truncstorei8", "truncstorei16", "store"]:  # TODO: more generic
                val, ptr = expr.operands
                # print("ptr", ptr)
                if isinstance(ptr, DAGOperand):
                    ptr_reg = str(ptr)
                    # print("ptr_reg", ptr_reg)
                    if ptr_reg in patterns:
                        pre = list(patterns.keys()).index(ptr_reg) < list(patterns.keys()).index(dest)
                        # print("pre", pre)
                        comp = patterns[ptr_reg]
                        # print("comp", comp)
                        if isinstance(comp, DAGBinary):
                            op_name = comp.name
                            # print("op_name", op_name)
                            if op_name in ["add", "sub"]:
                                # print("A")
                                lhs, rhs = comp.operands
                                if str(lhs) == ptr_reg:  # TODO: also allow swap for +
                                    # print("IF")
                                    new_name = expr.name
                                    if "truncstore" in new_name:
                                        new_name = new_name.replace("store", "st")
                                    prefix = "pre" if pre else "post"
                                    new_name = f"{prefix}_{new_name}"
                                    new_op = DAGTernary(new_name, val, ptr, rhs)
                                    patterns[ptr_reg] = new_op
                                    # print("ASSIGNED")
                                    del patterns[dest]
                                    break


    context.patterns = patterns
    # input("abc")

    # return self, None
    return self


def block(self: behav.Block, context):
    # print("block", self)

    stmts = []
    ret_ = []

    for stmt in self.statements:
        stmt, ret = stmt.generate(context)
        if isinstance(stmt, behav.Conditional):
            if len(stmt.conds) == 1:
                if isinstance(stmt.stmts[0], behav.Block):
                    if len(stmt.stmts[0].statements) == 0:
                        continue
        stmts.append(stmt)
        ret_.append(ret)

    self.statements = stmts

    return self, ret_


def binary_operation(self: behav.BinaryOperation, context: "DAGBuilderContext"):
    # print("binary_operation")
    op_name = LOOKUP.get(self.op.value, "UNKNOWN")

    # TODO: remove this hacks
    # if self.op.value == "%":
    #       if isinstance(self.right, behav.NumberLiteral):
    #           if self.right.value == 32:
    #           self.left.generate(context)
    #           return self.left
    # elif self.op.value == "!=":
    #   if isinstance(self.right, behav.NumberLiteral):
    #       if self.right.value == 0:
    #           # self.left.generate(context)
    #           lit = behav.IntLiteral(1)
    #           lit.generate(context)  # Will this work?
    #           return lit

    # input("qqq")

    _, left_ = self.left.generate(context)

    _, right_ = self.right.generate(context)

    if op_name == "srl":
        if isinstance(right_, DAGImm):
            # needs explicit type
            ty_name = "i32"  # TODO: do not hardcode
            right_ = DAGUnary(ty_name, right_)

    ret_ = DAGBinary(op_name, left_, right_)
    return self, ret_

def slice_operation(self: behav.SliceOperation, context: "DAGBuilderContext"):
    # print("slice_operation")
    # ref_ = None
    # for ann in self.annotations:
    #     ref_ = ann
    #     break

    _, expr_ = self.expr.generate(context)

    _, left_ = self.left.generate(context)

    _, right_ = self.right.generate(context)

    # raise NotImplementedError("Dynamic slices not supported")
    ret_ = DAGTernary("slice", expr_, left_, right_)  # TODO
    return self, ret_

def concat_operation(self: behav.ConcatOperation, context: "DAGBuilderContext"):
    # print("concat_operation")
    context.print("concat_operation")

    self.left.generate(context)

    self.right.generate(context)

    return self, None

def number_literal(self: behav.IntLiteral, context: "DAGBuilderContext"):
    ret_ = DAGImm(self.value)
    return self, ret_

def int_literal(self: behav.IntLiteral, context: "DAGBuilderContext"):
    return self, None

def scalar_definition(self: behav.ScalarDefinition, context: "DAGBuilderContext"):
    return self, None

def assignment(self: behav.Assignment, context: "DAGBuilderContext"):
    # print("assignment")
    # if isinstance(self.target, behav.ScalarDefinition):
    #       context.assignments[self.target] = self.expr
    #       return



  # There are no nested assignments, therefore this should work in theory
    # for register reads/writes and memory loads/stores
    ret_ = None

    context.is_write = True
    target, target_ = self.target.generate(context)
    # print("target_", target_)

    context.is_write = False

    context.is_read = True
    expr, expr_ = self.expr.generate(context)
    # print("expr_", expr_)
    context.is_read = False

    if isinstance(target_, DAGUnary):
        if "dummy_store" in target_.name:
            new_name = target_.name.replace("dummy_", "")
            ty = expr.inferred_type
            assert ty is not None
            assert isinstance(ty, arch.IntegerType)
            signed = ty.signed
            width = ty.width
            out_type = f"i{width}"
            if isinstance(expr_, DAGUnary):
                if expr_.name == out_type:
                    expr_ = expr_.operands[0]

            if width == 32:  # TODO: do not hardcode XLEN
                pass
            elif width in [8, 16]:
                new_name += out_type
                new_name = "trunc" + new_name
            else:
                raise NotImplementedError

            ret_ = DAGBinary(new_name, expr_, target_.operands[0])
    if not ret_:
        ret_ = DAGAssignment(target_, expr_)
    # print("ret_", ret_)
    # input("@#")
    return self, ret_

def conditional(self: behav.Conditional, context: "DAGBuilderContext"):
    print("conditional")

    ret = self
    conds_ = []
    for cond in self.conds:
        context.is_read = True
        _, cond_ = cond.generate(context)
        context.is_read = False
        conds_.append(cond_)
        # if isinstance(ret, behav.IntLiteral):
        #   assert len(self.conds) == 1
        #   if not ret.signed and ret.value > 0:  # TODO
        #       ret = self.stmts[0][0].generate(context)  # TODO
        #   else:
        #       ret = self.stmts[1][0].generate(context)  # TODO
        #   break
        # print("ret3", ret)
        # input("?????")

    if ret == self:
        print("ret == self")
        for op in self.stmts:
            print("op", op)
            # print("op", op)
            # for stmt in flatten(op):
            # print("stmt", stmt)
            stmt = op
            _, stmt_ = stmt.generate(context)
            if isinstance(stmt_, list):
                assert len(stmt_) == 1
                stmt_ = stmt_[0]
            print("stmt_", stmt_)
            is_branch = False
            is_conditional = True
            is_relative = False
            if isinstance(stmt_, DAGAssignment):
                print("if DAGAssignment")
                if isinstance(stmt_.target, DAGOperand):
                    print("if DAGOperand")
                    if stmt_.target.name == "PC":
                        print("if PC")
                        is_branch = True
                        if isinstance(stmt_.expr, DAGTernary) and stmt_.expr.name == "slice":
                            # this nis a hack t orun this pass after adding explicit truncations...
                            expr = stmt_.expr.operands[0]
                        else:
                            expr = stmt_.expr
                        if isinstance(expr, DAGBinary):
                            print("if DAGBinary")
                            if expr.name == "add":
                                print("if add")
                                # TODO: allow swapped lhs and rhs + sub
                                lhs, rhs = expr.operands
                                if isinstance(lhs, DAGOperand):
                                    print("if DAGoperand")
                                    if lhs.name == "PC":
                                        print("if PC")
                                        is_relative = True
                                        assert len(conds_) == 1
                                        assert isinstance(conds_[0], DAGBinary)
                                        cmp_name = conds_[0].name
                                        assert cmp_name in ["seteq", "setne", "setlt", "setgt", "setle", "setge"]
                                        cmp_name = cmp_name.upper()
                                        lhs_, rhs_ = conds_[0].operands
                                        new_op_name = "riscv_brcc"
                                        new_op = DAGQuaternary(new_op_name, lhs_, rhs_, cmp_name, rhs)
                                        # print("new_op", new_op)
                                        return ret, new_op
                # print("stmt_.target", stmt_.target)
                # print("stmt_.expr", stmt_.expr)
                # if stmts.target
            # input("aaa")

    return ret, None

def loop(self: behav.Loop, context: "DAGBuilderContext"):

    context.is_read = True
    self.cond.generate(context)
    context.is_read = False
    self.stmts = [x.generate(context) for x in self.stmts]
    return self, None

def ternary(self: behav.Ternary, context: "DAGBuilderContext"):

    self.cond.generate(context)

    self.then_expr.generate(context)

    self.else_expr.generate(context)

    return self, None

def return_(self: behav.Return, context: "DAGBuilderContext"):

    if self.expr is not None:
        self.expr.generate(context)

    return self, None

def unary_operation(self: behav.UnaryOperation, context: "DAGBuilderContext"):
    # print("unary_operation")
    op_name = LOOKUP.get(self.op.value, "UNKNOWN")

    _, right_ = self.right.generate(context)

    ret_ = DAGUnary(op_name, right_)
    return self, ret_

def named_reference(self: behav.NamedReference, context: "DAGBuilderContext"):
    # print("named_reference")
    if ":" in self.reference.name:
        ty, name = self.reference.name.split(":", 1)
        if "$" in name:
            name = name[1:]
    elif isinstance(self.reference, arch.Memory):
        ty = "pc" if arch.MemoryAttribute.IS_PC in self.reference.attributes else "?"
        name = self.reference.name
    else:
        name = self.reference.name
        ty = "?"
    ret_ = DAGOperand(name, DAGType(ty))
    # if "GPR" in self.reference.name:
    # else:
    # print("NOT GPR", self.reference.name)
    ret = self
    # for key, value in context.assignments.items():
    #       if isinstance(key, behav.ScalarDefinition):
    #       if key.scalar.name == self.reference.name:
    #           print("key", key, key.scalar)
    #           print("value", value)
    #           input("?")
    #           ret = value
    if ret == self:
        pass
    else:
        ret.generate(context)

    # print("ret_", ret_)
    return ret, ret_

def indexed_reference(self: behav.IndexedReference, context: "DAGBuilderContext"):
    # print("indexed_reference")
    # print("dir", dir(self.reference), self.reference.attributes)
    # def check_gpr(node: behav.IndexedReference):
    #       ref = node.reference
    assert isinstance(self.reference, arch.Memory)
    name = self.reference.name
    ret_ = None
    if arch.MemoryAttribute.IS_MAIN_MEM in self.reference.attributes:
        new_op = None
        if context.is_write:
            # print("STORE")
            new_op = "dummy_store" # missing value!
            context.may_store = True
            # input("~")
        elif context.is_read:
            # print("LOAD")
            new_op = "load"
            context.may_load = True
        # print("self.index", self.index)
        _, index_ = self.index.generate(context)
        assert index_ is not None
        if isinstance(index_, DAGBinary):
            if index_.name == "add":
                op_name = None
                lhs, rhs = index_.operands
                lhs_type = None
                if isinstance(lhs, DAGOperand):
                    lhs_type = lhs.ty.name
                rhs_type = None
                if isinstance(rhs, DAGOperand):
                    rhs_type = rhs.ty.name
                if lhs_type == "GPR" and rhs_type == "GPR":
                    op_name = "AddrRegReg"
                    context.complex_patterns.append("AddrRegReg")
                elif lhs_type == "GPR" and rhs_type == "simm12":  # TODO: check if non 12 bit allowed?
                    op_name = "AddrRegImm"
                    context.complex_patterns.append("AddrRegImm")
                elif rhs_type == "GPR" and lhs_type == "simm12":
                    op_name = "AddrRegImm"
                    context.complex_patterns.append("AddrRegImm")
                    lhs, rhs = rhs, lhs # spwap
                else:
                    raise NotImplementedError

                assert op_name is not None
                index_ = DAGBinary(op_name, lhs, rhs)  # TODO: COMPLEX
                # print("index_", index_)

        if new_op:
            ret_ = DAGUnary(new_op, index_)
            # print("ret_", ret_)
            # input("123")
    elif arch.MemoryAttribute.IS_MAIN_REG in self.reference.attributes:
        pass  # handled in IndexedReference (should eliminate Index?)  # TODO
    else:  # CSR, custom memory,...
        raise NotImplementedError(f"Unhandled reference: {name} (Side effects?)")

    #   return arch.MemoryAttribute.IS_MAIN_REG in ref.attributes  # or ref.name == "X"
    # is_gpr = check_gpr(self)
    # if not is_gpr:
    #   context.has_side_effects = True

    # context.print("> is_gpr", is_gpr)


    # if is_gpr:
    #   if context.is_write:
    #           context.writes.append(self.index.reference.name)
    # elif context.is_read:
    #   context.reads.append(self.index.reference.name)
    # else:
    #       raise NotImplementedError
    self.index.generate(context)
    # self.right.generate(context)

    return self, ret_

def type_conv(self: behav.TypeConv, context: "DAGBuilderContext"):

    target_size = self.size
    if target_size is None:
        ty = self.inferred_type
        assert ty is not None
        target_size = ty.width
    sign_letter = "?"
    signed = None
    if self.data_type in [arch.DataType.S, arch.DataType.U]:
        signed = self.data_type == arch.DataType.S
        if self.data_type == arch.DataType.S:
            sign_letter = "s"
            sign_letter_ = "i"
        elif self.data_type == arch.DataType.U:
            sign_letter = "u"
            # sign_letter_ = "u"
            sign_letter_ = "i"
    # for ann in self.annotations:
    #     if "sext_inreg" in ann:
    #         sign_letter = ann


    print("self.expr", self.expr)
    _, expr_ = self.expr.generate(context)
    ret_ = None
    assert expr_ is not None
    if isinstance(expr_, DAGUnary):
        if expr_.name == "load":
            assert signed is not None
            load_op = None
            assert target_size is not None
            load_op = "load"
            if target_size == 32:  # TODO: do not hardcode!
                pass
            elif target_size in [8, 16]:
                load_op = "ext" + load_op
                load_op += f"i{target_size}"
                if signed:
                    load_op = "s" + load_op
                else:
                    load_op = "z" + load_op
                    # TODO: also implement extloadi8! (ALT)
            else:
                raise NotImplementedError
            ret_ = expr_
            ret_.name = load_op
            # print("LD")
        # input("++")
    else:
        pass
        # for ann in self.annotations:
        #     if "sext_inreg" in ann:
        #         sign_letter = ann
        #         op_name, ty =  ann.split(" ", 1)
        #         ret_ = DAGBinary(op_name, expr_, ty)
    if ret_ is None:
        cast_op = sign_letter_ + str(target_size)
        ret_ = DAGUnary(cast_op, expr_)
    # print("ret_", ret_)
    # input("333")
    return self, ret_

def callable_(self: behav.Callable, context: "DAGBuilderContext"):

    for arg, arg_descr in zip(self.args, self.ref_or_name.args):
        arg.generate(context)

    return self, None

def group(self: behav.Group, context: "DAGBuilderContext"):
    _, ret_ = self.expr.generate(context)

    return self, ret_
