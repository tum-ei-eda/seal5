# SPDX-License-Identifier: Apache-2.0
"""Verify branch recognition retains the condition and displacement."""

import unittest

from m2isar.metamodel import behav

from test_explicit_names import symbol
from test_normalize_subscripts import render
from seal5.model import DataType, Seal5ImmOperand, Seal5Type
from seal5.transform.detect_branches import BranchIntrinsic, detect_branch


def branch_tree(operator="=="):
    pc = symbol("PC", 64)
    immediate = symbol("imm", 13)
    registers = symbol("X", 64)
    lhs = behav.IndexedReference(registers, behav.Literal(1))
    rhs = behav.IndexedReference(registers, behav.Literal(2))
    condition = behav.BinaryOperation(lhs, behav.Operator(operator), rhs)
    offset = behav.NamedReference(immediate)
    value = behav.BinaryOperation(behav.NamedReference(pc), behav.Operator("+"), offset)
    assignment = behav.Assignment(behav.NamedReference(pc), value)
    conditional = behav.Conditional([condition], [behav.Block([assignment])])
    operation = behav.Operation([conditional])
    operands = {"imm": Seal5ImmOperand("imm", Seal5Type(DataType.S, 13, 1), {}, [])}
    return operation, operands, condition, offset


class BranchTests(unittest.TestCase):
    def test_branch_displacement_is_an_input(self):
        from seal5.transform.detect_inouts.collect import VisitorContext
        from seal5.transform.detect_inouts.visitor import DetectInoutsVisitor

        original, operands, _, _ = branch_tree()
        lowered, _ = detect_branch(original, operands)
        context = VisitorContext()
        DetectInoutsVisitor().generate(lowered, context)
        self.assertIn("imm", context.reads)
        self.assertFalse(context.writes)

    def test_trap_collection_keeps_the_aligned_branch(self):
        from m2isar.metamodel import arch, type_info
        from seal5.transform.collect_raises.collect import VisitorContext as RaiseContext
        from seal5.transform.collect_raises.visitor import CollectRaisesVisitor
        from seal5.transform.detect_inouts.collect import VisitorContext
        from seal5.transform.detect_inouts.visitor import DetectInoutsVisitor

        original, operands, _, offset = branch_tree()
        outer = original.statements[0]
        update = outer.stmts[0]
        function = arch.Function("raise", {}, None, type_info.TypeKind.VOID, [], None, extern=True)
        trap = behav.ProcedureCall(function, [])
        misaligned = behav.BinaryOperation(offset, behav.Operator("%"), behav.Literal(4))
        outer.stmts = [behav.Block([behav.Conditional([misaligned], [behav.Block([trap]), update])])]
        lowered, name = detect_branch(original, operands)
        self.assertEqual(name, "imm")
        raises = RaiseContext()
        lowered = CollectRaisesVisitor().generate(lowered, raises)
        self.assertEqual(len(raises.raises), 1)
        context = VisitorContext()
        lowered = DetectInoutsVisitor().generate(lowered, context)
        guard = lowered.statements[0].stmts[0].statements[0]
        self.assertEqual(guard.stmts[0].statements, [])
        self.assertIsInstance(guard.stmts[1].statements[0], BranchIntrinsic)
        self.assertIn("imm", context.reads)

    def test_empty_trap_arm_survives_analysis(self):
        from seal5.transform.collect_raises.collect import VisitorContext as RaiseContext
        from seal5.transform.collect_raises.visitor import CollectRaisesVisitor
        from seal5.transform.detect_side_effects.collect import VisitorContext as SideContext
        from seal5.transform.detect_side_effects.visitor import DetectSideEffectsVisitor
        from seal5.transform.detect_calls.collect import VisitorContext as CallContext
        from seal5.transform.detect_calls.visitor import DetectCallsVisitor
        from seal5.transform.detect_loops.collect import VisitorContext as LoopContext
        from seal5.transform.detect_loops.visitor import DetectLoopsVisitor
        from seal5.transform.detect_inouts.collect import VisitorContext
        from seal5.transform.detect_inouts.visitor import DetectInoutsVisitor

        original, operands, _, offset = branch_tree()
        outer = original.statements[0]
        misaligned = behav.BinaryOperation(offset, behav.Operator("%"), behav.Literal(4))
        guard = behav.Conditional([misaligned], [behav.Block([]), outer.stmts[0]])
        outer.stmts = [behav.Block([guard])]
        for visitor, context in (
            (CollectRaisesVisitor(), RaiseContext()),
            (DetectSideEffectsVisitor(), SideContext()),
            (DetectInoutsVisitor(), VisitorContext()),
            (DetectCallsVisitor(), CallContext()),
            (DetectLoopsVisitor(), LoopContext()),
        ):
            original = visitor.generate(original, context)
            self.assertIs(original.statements[0].stmts[0].statements[0], guard)
            self.assertIsInstance(guard.stmts[1].statements[0], behav.Assignment)
        lowered, name = detect_branch(original, operands)
        self.assertEqual(name, "imm")
        lowered_guard = lowered.statements[0].stmts[0].statements[0]
        self.assertIs(lowered_guard.conds[0], misaligned)
        self.assertIsInstance(lowered_guard.stmts[1].statements[0], BranchIntrinsic)

    def test_alignment_guard_is_preserved(self):
        original, operands, condition, offset = branch_tree()
        outer = original.statements[0]
        update = outer.stmts[0]
        trap = behav.ProcedureCall("raise", [])
        misaligned = behav.BinaryOperation(offset, behav.Operator("%"), behav.Literal(4))
        guard = behav.Conditional([misaligned], [behav.Block([trap]), update])
        outer.stmts = [behav.Block([guard])]
        lowered, name = detect_branch(original, operands)
        self.assertEqual(name, "imm")
        lowered_guard = lowered.statements[0].stmts[0].statements[0]
        self.assertIs(lowered_guard.conds[0], misaligned)
        self.assertIs(lowered_guard.stmts[0].statements[0], trap)
        self.assertIsInstance(lowered_guard.stmts[1].statements[0], BranchIntrinsic)
        self.assertIsInstance(update.statements[0], behav.Assignment)

        def execute(tree, rs1, rs2, displacement):
            state = {"PC": 128, "imm": displacement, "traps": 0}

            def evaluate(expr):
                if isinstance(expr, behav.Literal):
                    return expr.value
                if isinstance(expr, behav.NamedReference):
                    return state[expr.reference.name]
                if isinstance(expr, behav.IndexedReference):
                    return {1: rs1, 2: rs2}[evaluate(expr.index)]
                if isinstance(expr, behav.BinaryOperation):
                    lhs, rhs = evaluate(expr.left), evaluate(expr.right)
                    return {"==": lambda: lhs == rhs, "%": lambda: lhs % rhs, "+": lambda: lhs + rhs}[expr.op.value]()
                raise AssertionError(type(expr))

            def visit(node):
                if isinstance(node, behav.Operation):
                    for stmt in node.statements:
                        visit(stmt)
                elif isinstance(node, behav.Conditional):
                    if evaluate(node.conds[0]):
                        visit(node.stmts[0])
                    elif len(node.stmts) == 2:
                        visit(node.stmts[1])
                elif isinstance(node, BranchIntrinsic):
                    if evaluate(node.args[0]):
                        state["PC"] += evaluate(node.offset)
                elif isinstance(node, behav.Assignment):
                    state[node.target.reference.name] = evaluate(node.expr)
                elif isinstance(node, behav.ProcedureCall):
                    state["traps"] += 1
                else:
                    raise AssertionError(type(node))

            visit(tree)
            return state

        for rs1, rs2 in ((5, 5), (5, 6)):
            for displacement in (-4, -2, 0, 2, 4):
                self.assertEqual(execute(original, rs1, rs2, displacement), execute(lowered, rs1, rs2, displacement))

    def test_conditions_and_displacement(self):
        for operator in ("==", "!=", "<", ">=", "&"):
            original, operands, condition, offset = branch_tree(operator)
            result, name = detect_branch(original, operands)
            self.assertEqual(name, "imm")
            call = result.statements[0]
            self.assertIsInstance(call, BranchIntrinsic)
            self.assertIs(call.args[0], condition)
            self.assertIs(call.offset, offset)
            self.assertEqual(render(call), f"branch((X[1]) {operator} (X[2]))")
            self.assertIs(detect_branch(result, operands)[0], result)

    def test_condition_immediate_is_distinct_from_destination(self):
        for name, width in (("constant", 5), ("limit", 3), ("threshold", 8)):
            original, operands, condition, offset = branch_tree()
            immediate = behav.NamedReference(symbol(name, width))
            condition.right = immediate
            operands[name] = Seal5ImmOperand(name, Seal5Type(DataType.S, width, 1), {}, [])
            lowered, destination = detect_branch(original, operands)
            self.assertEqual(destination, "imm")
            self.assertIs(lowered.statements[0].args[0].right, immediate)
            self.assertIs(lowered.statements[0].offset, offset)

    def test_other_effects_are_not_discarded(self):
        original, operands, _, _ = branch_tree()
        original.statements.append(behav.ProcedureCall("raise", []))
        self.assertIs(detect_branch(original, operands)[0], original)

    def test_else_and_traps_are_not_discarded(self):
        original, operands, _, _ = branch_tree()
        conditional = original.statements[0]
        conditional.stmts.append(behav.Block([behav.ProcedureCall("raise", [])]))
        self.assertIs(detect_branch(original, operands)[0], original)

    def test_unknown_immediate_is_not_lowered(self):
        original, _, _, _ = branch_tree()
        self.assertIs(detect_branch(original, {})[0], original)


if __name__ == "__main__":
    unittest.main()
