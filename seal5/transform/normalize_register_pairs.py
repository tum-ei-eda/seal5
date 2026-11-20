# SPDX-License-Identifier: Apache-2.0
"""Expose RV32 pair values to PatternGen without changing architectural state.

Run on an emission-only copy after operand classification. XP is a logical
64-bit view of an explicitly marked even/odd X pair, not a new register bank.
"""
from copy import copy

from m2isar.metamodel import arch, behav
from m2isar.metamodel.type_info import PrimitiveType, TypeKind

from seal5.transform.explicit_names import ExplicitNames, ungroup


class NormalizeRegisterPairs(ExplicitNames):
    def __init__(self, pair_names):
        super().__init__(32)
        self.pair_names = set(pair_names)

    def _index(self, expr):
        expr = ungroup(expr)
        if isinstance(expr, behav.NamedReference) and isinstance(expr.reference, arch.BitFieldDescr):
            if expr.reference.name in self.pair_names:
                return expr, 0
        if isinstance(expr, behav.BinaryOperation) and expr.op.value == "+":
            left, right = ungroup(expr.left), ungroup(expr.right)
            if isinstance(left, behav.Literal):
                left, right = right, left
            base = self._index(left)
            if base and isinstance(right, behav.Literal):
                return base[0], base[1] + right.value
        return None

    def _word(self, expr):
        expr = ungroup(expr)
        if not isinstance(expr, behav.IndexedReference) or expr.right is not None:
            return None
        if expr.reference.name != "X" or expr.reference.ty.element_type.size != 32:
            return None
        index = self._index(expr.index)
        if index and index[1] not in (0, 1):
            raise ValueError("A register pair contains only word offsets zero and one")
        return (expr, *index) if index else None

    @staticmethod
    def _same_index(left, right):
        return left.reference is right.reference

    def _pair(self, word):
        original, index, _ = word
        result = copy(original)
        result.reference = copy(original.reference)
        result.reference.name = "XP"
        result.reference.ty = copy(original.reference.ty)
        result.reference.ty.element_type = PrimitiveType(TypeKind.UINT, 64)
        result.index = index
        result.ty = PrimitiveType(TypeKind.UINT, 64)
        self.changed += 1
        return result

    def _store(self, first, second):
        # Merge only adjacent writes of a complete, already-evaluated 64-bit
        # local value. Combining arbitrary RHS expressions could change aliasing
        # or evaluation order when the second reads the first word's result.
        if not isinstance(first, behav.Assignment) or not isinstance(second, behav.Assignment):
            return None
        lo, hi = self._word(first.target), self._word(second.target)
        if not lo or not hi or lo[2] != 0 or hi[2] != 1 or not self._same_index(lo[1], hi[1]):
            return None
        low, high = ungroup(first.expr), ungroup(second.expr)
        if not isinstance(low, behav.SliceOperation) or not isinstance(high, behav.SliceOperation):
            return None
        parts = [ungroup(x) for x in (low.left, low.right, high.left, high.right)]
        if not all(isinstance(x, behav.Literal) for x in parts) or [x.value for x in parts] != [31, 0, 63, 32]:
            return None
        a, b = ungroup(low.expr), ungroup(high.expr)
        if not isinstance(a, behav.NamedReference) or not isinstance(b, behav.NamedReference):
            return None
        if not isinstance(a.reference, arch.Variable) or a.reference is not b.reference:
            return None
        if a.reference.ty.size != 64:
            return None
        return behav.Assignment(self._pair(lo), a, first.line_info)

    def generate(self, expr, context=None):
        if isinstance(expr, list):
            statements, i = [], 0
            while i < len(expr):
                merged = self._store(expr[i], expr[i + 1]) if i + 1 < len(expr) else None
                statements.append(self.generate(merged if merged is not None else expr[i], context))
                i += 2 if merged is not None else 1
            return statements
        if isinstance(expr, behav.ConcatOperation):
            hi, lo = self._word(expr.left), self._word(expr.right)
            if hi and lo and hi[2] == 1 and lo[2] == 0 and self._same_index(hi[1], lo[1]):
                return self._pair(lo)
        word = self._word(expr)
        if word:
            base = word[2] * 32
            result = behav.SliceOperation(self._pair(word), behav.Literal(base + 31), behav.Literal(base))
            result.ty = PrimitiveType(TypeKind.UINT, 32)
            return result
        return super().generate(expr, context)
