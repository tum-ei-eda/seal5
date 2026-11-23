# SPDX-License-Identifier: Apache-2.0
"""Lower declared XP views to shared X storage for architectural exports."""
from copy import deepcopy
from m2isar.metamodel import arch, behav
from m2isar.metamodel.type_info import PrimitiveType, TypeKind
from seal5.register_pairs import is_pair_bank, validate_pair_bank
from seal5.transform.explicit_names import ExplicitNames, ungroup


class LowerRegisterPairViews(ExplicitNames):
    def __init__(self, registers, reserved=()):
        super().__init__(32)
        self.registers = registers
        self.reserved = set(reserved)
        self.serial = 0

    def pair(self, expr):
        expr = ungroup(expr)
        return expr if isinstance(expr, behav.IndexedReference) and is_pair_bank(expr.reference) else None

    def word(self, pair, high=False):
        validate_pair_bank(pair.reference, self.registers)
        base = deepcopy(pair.index)
        if high:
            base = behav.BinaryOperation(base, behav.Operator("+"), behav.Literal(1))
        return behav.IndexedReference(self.registers["X"], base)

    def generate(self, expr, context=None):
        if isinstance(expr, behav.Assignment) and (pair := self.pair(expr.target)):
            while (name := f"_seal5_pair_value_{self.serial}") in self.reserved:
                self.serial += 1
            self.reserved.add(name)
            value = arch.Variable(name, PrimitiveType(TypeKind.UINT, 64), {})
            ref = behav.NamedReference(value)
            stores = [
                behav.Assignment(
                    self.word(pair, high),
                    behav.SliceOperation(ref, behav.Literal(63 if high else 31), behav.Literal(32 if high else 0)),
                )
                for high in (False, True)
            ]
            return behav.Block(
                [
                    behav.Assignment(behav.VarDefinition(value), self.generate(expr.expr)),
                    behav.Conditional(
                        [behav.BinaryOperation(deepcopy(pair.index), behav.Operator("!="), behav.Literal(0))],
                        [behav.Block(stores)],
                    ),
                ]
            )
        if pair := self.pair(expr):
            result = behav.Ternary(
                behav.BinaryOperation(deepcopy(pair.index), behav.Operator("=="), behav.Literal(0)),
                behav.Literal(0),
                behav.ConcatOperation(self.word(pair, True), self.word(pair)),
            )
            result.ty = PrimitiveType(TypeKind.UINT, 64)
            result.then_expr.ty = PrimitiveType(TypeKind.UINT, 64)
            return result
        return super().generate(expr, context)
