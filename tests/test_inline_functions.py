# SPDX-License-Identifier: Apache-2.0
"""Inline helper returns without sharing or corrupting their expression trees."""

import unittest
from types import SimpleNamespace

from m2isar.metamodel import arch, behav, type_info

from seal5.model import Seal5FunctionAttribute
from seal5.transform.inline_functions.visitor import InlineFunctionsVisitor


class InlineFunctionTests(unittest.TestCase):
    def function(self, body=None, name="identity"):
        ty = type_info.PrimitiveType(type_info.TypeKind.UINT, 32)
        param = arch.FnParam("x", ty)
        body = behav.Return(behav.NamedReference(param)) if body is None else body
        return arch.Function(
            name,
            {Seal5FunctionAttribute.INLINE: []},
            16,
            type_info.TypeKind.UINT,
            [param],
            behav.Operation([body]),
        )

    def test_return_is_inlined_with_declared_width_and_independent_calls(self):
        function = self.function()
        context = SimpleNamespace(functions={function.name: function})
        visitor = InlineFunctionsVisitor()
        results = [visitor.generate(behav.Callable(function.name, [behav.Literal(n)]), context) for n in [7, 9]]
        self.assertEqual([value.expr.expr.value for value in results], [7, 9])
        for result in results:
            self.assertIsInstance(result, behav.TypeConv)
            self.assertEqual(result.size, 16)
            self.assertEqual(result.expr.size, 32)
        self.assertIsInstance(function.operation.statements[0].expr, behav.NamedReference)
        self.assertIsNot(results[0].expr, results[1].expr)
        results[0].expr = behav.Literal(11)
        self.assertEqual(results[1].expr.expr.value, 9)

    def test_repeated_parameter_uses_have_independent_trees(self):
        function = self.function()
        param = function.args["x"]
        function.operation.statements[0].expr = behav.BinaryOperation(
            behav.NamedReference(param), behav.Operator("+"), behav.NamedReference(param)
        )
        result = InlineFunctionsVisitor().generate(
            behav.Callable(function.name, [behav.Literal(3)]), SimpleNamespace(functions={function.name: function})
        )
        self.assertIsNot(result.expr.left, result.expr.right)
        self.assertEqual(result.expr.left.expr.value, 3)
        self.assertEqual(result.expr.right.expr.value, 3)

    def test_single_return_block_is_supported(self):
        function = self.function(behav.Block([behav.Return(behav.Literal(5))]))
        result = InlineFunctionsVisitor().generate(
            behav.Callable(function.name, [behav.Literal(0)]), SimpleNamespace(functions={function.name: function})
        )
        self.assertEqual(result.expr.value, 5)

    def test_unknown_external_and_recursive_helpers_remain_calls(self):
        visitor = InlineFunctionsVisitor()
        call = behav.Callable("unknown", [])
        self.assertIs(visitor.generate(call, SimpleNamespace(functions={})), call)
        function = self.function()
        function.extern = True
        call = behav.Callable(function.name, [behav.Literal(1)])
        self.assertIs(visitor.generate(call, SimpleNamespace(functions={function.name: function})), call)
        function.extern = False
        function.operation.statements = [behav.Return(behav.Callable(function.name, [behav.Literal(1)]))]
        result = visitor.generate(call, SimpleNamespace(functions={function.name: function}))
        self.assertIsInstance(result.expr, behav.Callable)


if __name__ == "__main__":
    unittest.main()
