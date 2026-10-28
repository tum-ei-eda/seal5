# SPDX-License-Identifier: Apache-2.0
"""Recognize conditional PC-relative RISC-V branch behaviors."""

from copy import copy

from m2isar.metamodel import behav

from seal5.transform.explicit_names import ungroup


class BranchIntrinsic(behav.ProcedureCall):
    """Pattern-gen branch with its original displacement retained in the model.

    The reference parser consumes one argument and obtains the displacement
    from the operand marked ``is_branch_offs``.
    """

    def __init__(self, condition, offset, line_info=None):
        super().__init__("branch", [condition], line_info)
        self.offset = offset


def statements(expr):
    """Unwrap nested single blocks without discarding statements."""
    while isinstance(expr, behav.Operation):
        expr = expr.statements
    while isinstance(expr, list) and len(expr) == 1:
        child = expr[0]
        if isinstance(child, behav.Operation):
            expr = child.statements
        else:
            return child
    return expr


def strip_casts(expr):
    expr = ungroup(expr)
    while isinstance(expr, behav.TypeConv):
        expr = ungroup(expr.expr)
    return expr


def pc_relative_offset(expr):
    """Match PC = PC + immediate, accepting explicit XLEN/sign casts."""
    expr = statements(expr)
    if not isinstance(expr, behav.Assignment):
        return None
    target = ungroup(expr.target)
    if not isinstance(target, behav.NamedReference) or target.reference.name != "PC":
        return None
    value = strip_casts(expr.expr)
    if not isinstance(value, behav.BinaryOperation) or value.op.value != "+":
        return None
    for pc, offset in ((value.left, value.right), (value.right, value.left)):
        pc = ungroup(pc)
        if isinstance(pc, behav.NamedReference) and pc.reference is target.reference:
            immediate = strip_casts(offset)
            if isinstance(immediate, behav.NamedReference):
                return offset
    return None


def pure_condition(expr):
    """Only branch conditions composed of fields, literals and integer registers."""
    expr = ungroup(expr)
    if isinstance(expr, (behav.Literal, behav.NamedReference)):
        return True
    if isinstance(expr, behav.IndexedReference):
        return expr.reference.name in ("X", "XW") and expr.right is None and pure_condition(expr.index)
    if isinstance(expr, behav.TypeConv):
        return pure_condition(expr.expr)
    if isinstance(expr, behav.BinaryOperation):
        return (
            expr.op.value
            in ("+", "-", "*", "/", "%", "&", "|", "^", "<<", ">>", "==", "!=", "<", ">", "<=", ">=", "&&", "||")
            and pure_condition(expr.left)
            and pure_condition(expr.right)
        )
    if isinstance(expr, behav.UnaryOperation):
        return expr.op.value in ("!", "~", "+", "-") and pure_condition(expr.right)
    return False


def detect_branch(operation, operands):
    """Return a lowered operation, or the original if any behavior is unproven.

    Alignment traps may surround the intrinsic; their guards and effects are
    retained rather than assumed unreachable.
    """
    conditional = statements(operation)
    if not isinstance(conditional, behav.Conditional) or len(conditional.conds) != 1:
        return operation, None
    if len(conditional.stmts) != 1 or not pure_condition(conditional.conds[0]):
        return operation, None
    body = statements(conditional.stmts[0])
    guarded = False
    if (
        isinstance(body, behav.Conditional)
        and len(body.conds) == 1
        and len(body.stmts) == 2
        and pure_condition(body.conds[0])
    ):
        trap = statements(body.stmts[0])
        if isinstance(trap, behav.ProcedureCall):
            trap_name = trap.ref_or_name if isinstance(trap.ref_or_name, str) else trap.ref_or_name.name
            if trap_name == "raise":
                guarded = True
    update = statements(body.stmts[1]) if guarded else body
    offset = pc_relative_offset(update)
    if offset is None:
        return operation, None
    name = strip_casts(offset).reference.name
    if name not in operands:
        return operation, None
    from seal5.model import Seal5ImmOperand

    if not isinstance(operands[name], Seal5ImmOperand):
        return operation, None
    branch = BranchIntrinsic(conditional.conds[0], offset, conditional.line_info)
    if guarded:
        # Keep the taken-branch guard and the alignment check exactly as given.
        # Repeating a pure condition inside its true arm has the same outcome.
        def replace(node):
            if node is update:
                return branch
            if isinstance(node, list):
                return [replace(child) for child in node]
            if isinstance(node, behav.Operation):
                result = copy(node)
                result.statements = replace(node.statements)
                return result
            if isinstance(node, behav.Conditional):
                result = copy(node)
                result.stmts = replace(node.stmts)
                return result
            return node

        return replace(operation), name
    return behav.Operation([branch], operation.line_info), name
