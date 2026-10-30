# SPDX-License-Identifier: Apache-2.0
"""Compare array-range behavior before/after normalization, including aliasing."""

from copy import deepcopy
import unittest

from m2isar.metamodel import behav

from test_explicit_names import plus, symbol
from test_normalize_subscripts import render
from seal5.transform.normalize_subscripts import NormalizeSubscripts


class Interpreter:
    def __init__(self, storage, contents, variables=None):
        self.storage = storage
        self.contents = list(contents)
        self.variables = dict(variables or {})
        self.calls = 0

    def evaluate(self, expr):
        if isinstance(expr, behav.Group):
            return self.evaluate(expr.expr)
        if isinstance(expr, behav.Literal):
            return expr.value
        if isinstance(expr, behav.NamedReference):
            return self.variables[expr.reference.name]
        if isinstance(expr, behav.BinaryOperation):
            lhs, rhs = self.evaluate(expr.left), self.evaluate(expr.right)
            return lhs + rhs if expr.op.value == "+" else lhs - rhs
        if isinstance(expr, behav.IndexedReference):
            left = self.evaluate(expr.index)
            if expr.right is None:
                return self.contents[left]
            right = self.evaluate(expr.right)
            step = 1 if left < right else -1
            result = 0
            for address in range(left, right + step, step):
                result = (result << expr.reference.ty.element_type.size) | self.contents[address]
            return result
        if isinstance(expr, behav.ConcatOperation):
            return (self.evaluate(expr.left) << expr.right.ty.size) | self.evaluate(expr.right)
        if isinstance(expr, behav.SliceOperation):
            left, right = self.evaluate(expr.left), self.evaluate(expr.right)
            return (self.evaluate(expr.expr) >> min(left, right)) & ((1 << (abs(left - right) + 1)) - 1)
        if isinstance(expr, behav.FunctionCall):
            self.calls += 1
            return 0x01020304
        raise AssertionError(type(expr))

    def execute(self, expr):
        if isinstance(expr, behav.Operation):
            for stmt in expr.statements:
                self.execute(stmt)
            return
        if isinstance(expr, behav.Assignment):
            value = self.evaluate(expr.expr)
            if isinstance(expr.target, behav.VarDefinition):
                self.variables[expr.target.var.name] = value & ((1 << expr.target.var.ty.size) - 1)
                return
            target = expr.target
            left = self.evaluate(target.index)
            right = left if target.right is None else self.evaluate(target.right)
            step = 1 if left < right else -1
            width = target.reference.ty.element_type.size
            addresses = list(range(left, right + step, step))
            for number, address in enumerate(addresses):
                self.contents[address] = (value >> ((len(addresses) - number - 1) * width)) & ((1 << width) - 1)
            return
        raise AssertionError(type(expr))


class ArraySubscriptTests(unittest.TestCase):
    def test_reads_and_writes_in_both_directions(self):
        for name in ("MEM", "X", "local"):
            for width in (4, 8, 32):
                storage = symbol(name, width)
                address = behav.NamedReference(symbol("addr", 32))
                contents = [number & ((1 << width) - 1) for number in range(16)]
                for ascending in (False, True):
                    left, right = (address, plus(address, 3)) if ascending else (plus(address, 3), address)
                    access = behav.IndexedReference(storage, left, right)
                    visitor = NormalizeSubscripts(32)
                    lowered = visitor.generate(deepcopy(access))
                    original_vm = Interpreter(storage, contents, {"addr": 4})
                    lowered_vm = Interpreter(storage, contents, {"addr": 4})
                    self.assertEqual(original_vm.evaluate(access), lowered_vm.evaluate(lowered))
                    assignment = behav.Assignment(access, behav.Literal(0x123456789ABCDEF))
                    normalized = NormalizeSubscripts(32).generate(deepcopy(assignment))
                    original_vm.execute(assignment)
                    lowered_vm.execute(normalized)
                    self.assertEqual(original_vm.contents, lowered_vm.contents)

    def test_address_alias_and_rhs_evaluated_once(self):
        storage = symbol("X", 8)
        address = behav.IndexedReference(storage, behav.Literal(0))
        target = behav.IndexedReference(storage, address, plus(address, 3))
        original = behav.Assignment(target, behav.FunctionCall("next_value", []))
        lowered = NormalizeSubscripts(32).generate(deepcopy(original))
        for tree in (original, lowered):
            vm = Interpreter(storage, [0] * 8)
            vm.execute(tree)
            self.assertEqual(vm.contents, [1, 2, 3, 4, 0, 0, 0, 0])
            self.assertEqual(vm.calls, 1)

    def test_names_do_not_capture_source_variables(self):
        storage = symbol("local", 8)
        address = behav.NamedReference(symbol("_seal5_range_address_0", 32))
        original = behav.Assignment(behav.IndexedReference(storage, address, plus(address, 1)), behav.Literal(0x1234))
        normalized = NormalizeSubscripts(32).generate(original)
        self.assertNotEqual(normalized.statements[1].target.var.name, address.reference.name)
        self.assertIn(address.reference.name, render(normalized))

    def test_explicit_memory_option_and_idempotence(self):
        storage = symbol("MEM", 8)
        address = behav.NamedReference(symbol("addr", 32))
        original = behav.IndexedReference(storage, address, plus(address, 3))
        visitor = NormalizeSubscripts(32, memory=True)
        normalized = visitor.generate(original)
        self.assertEqual(render(normalized).count("MEM8["), 4)
        count = visitor.changed
        visitor.generate(normalized)
        self.assertEqual(visitor.changed, count)
        native = behav.IndexedReference(storage, plus(address, 3), address)
        self.assertEqual(render(visitor.generate(native)), "MEMX[addr]")


if __name__ == "__main__":
    unittest.main()
