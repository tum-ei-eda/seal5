# SPDX-License-Identifier: Apache-2.0
"""Explicit pattern-gen memory and register accesses.

These rewrites operate on behavior trees, without renaming the shared
architectural symbols. Bounds in CoreDSL are inclusive: MEM[a+1:a]
is a 16-bit access to a byte-addressed memory.
"""

from copy import copy

from m2isar.metamodel import behav
from m2isar.metamodel.type_info import ArrayType, PrimitiveType, TypeKind


def ungroup(expr):
    """Remove parentheses for matching, retaining them in the original tree."""
    while isinstance(expr, behav.Group):
        expr = expr.expr
    return expr


def affine(expr):
    """Return symbolic coefficients and a constant for side-effect-free indices.

    Symbol identity matters: two local variables with the same name need not
    denote the same storage. Reject calls and other potentially effectful nodes.
    """
    expr = ungroup(expr)
    if isinstance(expr, behav.Literal):
        return {}, int(expr.value)
    if isinstance(expr, behav.NamedReference):
        return {("name", id(expr.reference)): 1}, 0
    if isinstance(expr, behav.IndexedReference) and expr.right is None:
        # Register reads are pure; arbitrary memory reads may be volatile.
        if expr.reference.name not in ("X", "XW"):
            return None
        index = affine(expr.index)
        if index is not None:
            key = ("index", id(expr.reference), tuple(sorted(index[0].items())), index[1])
            return {key: 1}, 0
    if isinstance(expr, behav.BinaryOperation) and expr.op.value in ("+", "-"):
        lhs, rhs = affine(expr.left), affine(expr.right)
        if lhs is None or rhs is None:
            return None
        sign = 1 if expr.op.value == "+" else -1
        terms = dict(lhs[0])
        for symbol, coefficient in rhs[0].items():
            terms[symbol] = terms.get(symbol, 0) + sign * coefficient
        return {key: value for key, value in terms.items() if value}, lhs[1] + sign * rhs[1]
    return None


def distance(left, right):
    """Return the constant difference between two affine indices, if known."""
    lhs, rhs = affine(left), affine(right)
    if lhs is not None and rhs is not None and lhs[0] == rhs[0]:
        return lhs[1] - rhs[1]
    return None


class ExplicitNames:
    """Rewrite memory/register names independently; both options default off."""

    def __init__(self, xlen, *, memory=False, registers=False):
        if xlen not in (32, 64):
            raise ValueError(f"Unsupported RISC-V XLEN: {xlen}")
        self.xlen = xlen
        self.memory = memory
        self.registers = registers
        self.changed = 0

    def generate(self, expr, context=None):
        """Visit behavior children only, never following architectural references."""
        if isinstance(expr, list):
            return [self.generate(child, context) for child in expr]
        if not isinstance(expr, behav.BaseNode):
            return expr
        # References, types and source locations are metadata, not child nodes.
        for key, value in list(vars(expr).items()):
            if key not in ("reference", "ref_or_name", "ty", "line_info", "var"):
                if isinstance(value, (behav.BaseNode, list)):
                    setattr(expr, key, self.generate(value, context))
        if self.memory and isinstance(expr, behav.IndexedReference):
            return self._memory(expr)
        if self.registers and isinstance(expr, behav.SliceOperation):
            return self._register(expr)
        return expr

    def _memory(self, expr):
        ref = expr.reference
        if ref.name != "MEM" or not isinstance(ref.ty, ArrayType) or ref.ty.element_type.size != 8:
            return expr
        if expr.right is None:
            width, address = 8, expr.index
        else:
            delta = distance(expr.index, expr.right)
            # Ascending ranges reverse byte order and cannot use a native load.
            if delta is None or delta < 0:
                return expr
            width, address = 8 * (delta + 1), expr.right
        if width not in (8, 16, 32, 64):
            return expr
        result = copy(expr)
        result.reference = copy(ref)
        result.reference.name = "MEMX" if width == self.xlen else f"MEM{width}"
        result.reference.ty = copy(ref.ty)
        result.reference.ty.element_type = PrimitiveType(TypeKind.UINT, width)
        result.index, result.right = address, None
        result.ty = PrimitiveType(TypeKind.UINT, width)
        self.changed += 1
        return result

    def _register(self, expr):
        if self.xlen != 64 or distance(expr.left, behav.Literal(31)) != 0:
            return expr
        if distance(expr.right, behav.Literal(0)) != 0:
            return expr
        source = ungroup(expr.expr)
        if not isinstance(source, behav.IndexedReference) or source.reference.name != "X":
            return expr
        if source.right is not None:
            return expr
        result = copy(source)
        result.reference = copy(source.reference)
        result.reference.name = "XW"
        result.reference.ty = copy(source.reference.ty)
        result.reference.ty.element_type = PrimitiveType(TypeKind.UINT, 32)
        result.ty = PrimitiveType(TypeKind.UINT, 32)
        self.changed += 1
        return result
