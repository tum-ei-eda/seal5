# SPDX-License-Identifier: Apache-2.0
"""Recognize complete RV32 pair reads and safe adjacent pair writes."""
from m2isar.metamodel import behav
from seal5.transform.explicit_names import ExplicitNames
from seal5.transform.normalize_register_pairs import NormalizeRegisterPairs


class PairMatcher(NormalizeRegisterPairs):
    def _word(self, expr):
        try:
            return super()._word(expr)
        except ValueError:
            return None


class InferRegisterPairs(ExplicitNames):
    def __init__(self, operand_names):
        super().__init__(32)
        self.matcher = PairMatcher(operand_names)
        self.pairs = set()

    def generate(self, expr, context=None):
        if isinstance(expr, list):
            for first, second in zip(expr, expr[1:]):
                if merged := self.matcher._store(first, second):
                    self.pairs.add(merged.target.index.reference.name)
        if isinstance(expr, behav.ConcatOperation):
            hi, lo = self.matcher._word(expr.left), self.matcher._word(expr.right)
            if hi and lo and hi[2] == 1 and lo[2] == 0 and self.matcher._same_index(hi[1], lo[1]):
                self.pairs.add(lo[1].reference.name)
        return super().generate(expr, context)
