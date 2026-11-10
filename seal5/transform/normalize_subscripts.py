# SPDX-License-Identifier: Apache-2.0
"""Normalize scalar bit ranges and direction-sensitive address-space ranges.

CoreDSL scalar ranges are direction independent. Address-space ranges are
direction dependent. Native little-endian accesses can use explicit memory
names; remaining ranges use concatenations and element-wise stores.
"""

from copy import copy

from m2isar.metamodel import arch, behav
from m2isar.metamodel.type_info import ArrayType, PrimitiveType, TypeKind

from seal5.transform.explicit_names import ExplicitNames, affine, distance, ungroup


class IndexedPartSelect(behav.SliceOperation):
    """A scalar part select ``expr[base +: width]``.

    Keep the original inclusive bounds for generic analyses and diagnostics.
    """

    def __init__(self, original, base, width):
        super().__init__(original.expr, original.left, original.right, original.line_info)
        self.ty = original.ty
        self.base = base
        self.width = width


class NormalizeSubscripts(ExplicitNames):
    """Normalize fixed-width ranges, including array assignment targets."""

    def __init__(self, xlen, *, memory=False):
        super().__init__(xlen, memory=memory)
        self._depth = 0
        self._names = set()
        self._serial = 0

    def _collect_names(self, expr):
        if isinstance(expr, list):
            for child in expr:
                self._collect_names(child)
        elif isinstance(expr, behav.BaseNode):
            for field in ("reference", "var"):
                symbol = getattr(expr, field, None)
                if symbol is not None:
                    self._names.add(symbol.name)
            for key, value in vars(expr).items():
                if key not in ("reference", "ref_or_name", "ty", "line_info", "var"):
                    if isinstance(value, (behav.BaseNode, list)):
                        self._collect_names(value)

    def _variable(self, role, ty):
        while True:
            name = f"_seal5_range_{role}_{self._serial}"
            self._serial += 1
            if name not in self._names:
                self._names.add(name)
                return arch.Variable(name, ty, attributes={})

    @staticmethod
    def _range(expr):
        if not isinstance(expr, behav.IndexedReference) or expr.right is None:
            return None
        ty = expr.reference.ty
        if not isinstance(ty, ArrayType) or not isinstance(ty.element_type, PrimitiveType):
            return None
        delta = distance(expr.index, expr.right)
        if delta is None:
            return None
        return abs(delta) + 1, -1 if delta > 0 else 1, arch.get_const_or_val(ty.element_type.size)

    def _element(self, original, base, offset, width):
        index = base
        if offset:
            index = behav.BinaryOperation(base, behav.Operator("+" if offset > 0 else "-"), behav.Literal(abs(offset)))
        result = behav.IndexedReference(original.reference, index, line_info=original.line_info)
        result.ty = PrimitiveType(TypeKind.UINT, width)
        return self._memory(result) if self.memory else result

    def _array_read(self, expr, shape):
        count, step, width = shape
        result = self._element(expr, expr.index, 0, width)
        for number in range(1, count):
            element = self._element(expr, expr.index, step * number, width)
            result = behav.ConcatOperation(result, element, expr.line_info)
            result.ty = PrimitiveType(TypeKind.UINT, width * (number + 1))
        self.changed += 1
        # Parentheses preserve precedence when this range is itself subscripted.
        grouped = behav.Group(result, expr.line_info)
        grouped.ty = PrimitiveType(TypeKind.UINT, count * width)
        return grouped

    def _array_store(self, assignment, target, shape, context):
        count, step, width = shape
        address_type = getattr(target.index, "ty", None)
        if not isinstance(address_type, PrimitiveType) or not address_type.kind.is_int or address_type.size is None:
            address_type = PrimitiveType(TypeKind.UINT, self.xlen)
        address = self._variable("address", copy(address_type))
        value = self._variable("value", PrimitiveType(TypeKind.UINT, count * width))
        init_address = behav.Assignment(behav.VarDefinition(address), self.generate(target.index, context))
        init_value = behav.Assignment(behav.VarDefinition(value), self.generate(assignment.expr, context))
        stores = []
        for number in range(count):
            element = self._element(target, behav.NamedReference(address), step * number, width)
            high = (count - number) * width - 1
            low = high - width + 1
            part = behav.SliceOperation(behav.NamedReference(value), behav.Literal(high), behav.Literal(low))
            part.ty = PrimitiveType(TypeKind.UINT, width)
            stores.append(behav.Assignment(element, part, assignment.line_info))
        self.changed += 1
        return behav.Block([init_value, init_address, *stores], assignment.line_info)

    def generate(self, expr, context=None):
        if self._depth == 0:
            self._collect_names(expr)
        self._depth += 1
        try:
            return self._generate(expr, context)
        finally:
            self._depth -= 1

    def _generate(self, expr, context):
        if isinstance(expr, IndexedPartSelect):
            return expr
        if isinstance(expr, behav.Assignment):
            target = ungroup(expr.target)
            if self.memory and isinstance(target, behav.IndexedReference):
                named = self._memory(target)
                if named is not target:
                    expr.target = target = named
            shape = self._range(target)
            if shape is not None:
                return self._array_store(expr, target, shape, context)
        expr = super().generate(expr, context)
        shape = self._range(expr)
        if shape is not None:
            return self._array_read(expr, shape)
        if not isinstance(expr, behav.SliceOperation):
            return expr
        delta = distance(expr.left, expr.right)
        if delta is None:
            return expr
        lhs, rhs = affine(expr.left), affine(expr.right)
        if not lhs[0] and not rhs[0]:
            return expr  # Constant ranges are already accepted by pattern-gen.
        base = expr.right if delta >= 0 else expr.left
        self.changed += 1
        return IndexedPartSelect(expr, copy(base), abs(delta) + 1)
