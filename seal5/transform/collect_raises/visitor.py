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
	# self.stmts = [x.generate(context) for x in self.stmts]
	temp = []
	for i, stmt in enumerate(self.stmts):
		if i == 0:  # if
			cond = self.conds[i]
			temp.append(behav.UnaryOperation(behav.Operator("!"), cond))
		elif i < len(self.conds):  # elif
			cond = temp[0]
			for c in temp[1:]:
				cond = behav.BinaryOperation(cond, "&&", c)
			cond = behav.BinaryOperation(cond, "&&", self.conds[i])
		else:  # else
			assert i >= len(self.conds)
			assert len(temp) >= 1
			cond = temp[0]
			for c in temp[1:]:
				cond = behav.BinaryOperation(cond, "&&", c)
		context.cond_stack.append(cond)
		# print("before", context.cond_stack)
		self.stmts[i] = stmt.generate(context)
		# print("after", context.cond_stack)
		context.cond_stack.pop()

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

	return self

def indexed_reference(self: behav.IndexedReference, context):
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
	# print("procedure_call")

	fn_args = [arg.generate(context) for arg in self.args]

	# extract function object reference
	ref = self.ref_or_name if isinstance(self.ref_or_name, arch.Function) else None
	name = ref.name if isinstance(self.ref_or_name, arch.Function) else self.ref_or_name
	# print("name", name)
	# print("args", fn_args)
	if name == "raise":
		args = [arg.value for arg in fn_args]
		if len(context.cond_stack) == 0:
			cond = None
		else:
			cond = context.cond_stack[0]
			for c in context.cond_stack[1:]:
				cond = behav.BinaryOperation(cond, "&&", c)
		context.raises.append((cond, args))
