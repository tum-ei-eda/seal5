# SPDX-License-Identifier: Apache-2.0
"""The XP view contains sixteen RV32 pairs addressed by even register IDs."""
from m2isar.metamodel import arch, behav, type_info
from seal5.transform.explicit_names import ungroup

PAIR_ATTRIBUTE = "is_regpair"


def is_pair_bank(bank):
    return isinstance(bank, arch.RegisterBank) and PAIR_ATTRIBUTE in bank.attributes


def validate_pair_bank(bank, registers):
    if (
        bank.name != "XP"
        or bank.ty.element_type.size != 64
        or bank.ty.length != 32
        or bank.ty.element_type.kind != type_info.TypeKind.UINT
    ):
        raise ValueError("[[is_regpair]] requires register unsigned<64> XP[32]")
    base = registers.get("X")
    if base is None or base.ty.element_type.size != 32 or base.ty.length != 32:
        raise ValueError("XP requires an RV32 X[32] register bank")


def pair_index_operand(expr):
    """Recognize an encoded five-bit physical register ID, without remapping it."""
    expr = ungroup(expr)
    if isinstance(expr, behav.NamedReference) and isinstance(expr.reference, arch.BitFieldDescr):
        if expr.reference.ty.size == 5:
            return expr
    return None


def pair_operand_names(instruction):
    from seal5.model import Seal5OperandAttribute

    return {
        name
        for name, operand in instruction.operands.items()
        if operand.attributes.get(Seal5OperandAttribute.REG_CLASS) == "GPRPair"
    }


def legal_pair_operation(operation, pairs):
    """Specialize only proven parity checks for LLVM's even-only register class.

    The architectural tree is never modified; unknown checks remain intact.
    """
    from copy import deepcopy
    from seal5.transform.explicit_names import ExplicitNames

    def even(expr):
        expr = ungroup(expr)
        if isinstance(expr, behav.NamedReference) and isinstance(expr.reference, arch.BitFieldDescr):
            return expr.reference.name in pairs
        if isinstance(expr, behav.Literal):
            return expr.value & 1 == 0
        if isinstance(expr, behav.TypeConv):
            return even(expr.expr)
        if isinstance(expr, behav.BinaryOperation) and expr.op.value in ("|", "&", "^", "+", "-"):
            return even(expr.left) and even(expr.right)
        return False

    def constant(expr):
        expr = ungroup(expr)
        if isinstance(expr, behav.Literal):
            return expr.value
        if isinstance(expr, behav.TypeConv):
            value = constant(expr.expr)
            width = expr.size
            if value is None or width is None:
                return value
            if not isinstance(width, int) or width <= 0:
                return None
            value &= (1 << width) - 1
            if expr.data_type == type_info.TypeKind.INT and value & (1 << (width - 1)):
                value -= 1 << width
            return value
        if isinstance(expr, behav.BinaryOperation):
            a, b = constant(expr.left), constant(expr.right)
            if expr.op.value == "&" and ((b == 1 and even(expr.left)) or (a == 1 and even(expr.right))):
                return 0
            if a is not None and b is not None:
                ops = {
                    "!=": lambda: int(a != b),
                    "==": lambda: int(a == b),
                    "||": lambda: int(bool(a or b)),
                    "&&": lambda: int(bool(a and b)),
                    "|": lambda: a | b,
                    "&": lambda: a & b,
                    "^": lambda: a ^ b,
                }
                if expr.op.value in ops:
                    return ops[expr.op.value]()
        return None

    class Specialize(ExplicitNames):
        def generate(self, expr, context=None):
            if isinstance(expr, behav.Conditional) and len(expr.conds) == 1:
                value = constant(expr.conds[0])
                if value is not None:
                    branch = 0 if value else 1
                    return self.generate(expr.stmts[branch], context) if branch < len(expr.stmts) else behav.Block([])
            return super().generate(expr, context)

    return Specialize(32).generate(deepcopy(operation)) if pairs else operation
