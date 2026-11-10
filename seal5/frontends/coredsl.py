# SPDX-License-Identifier: Apache-2.0
"""CoreDSL set frontend accepting the explicit pattern-gen vocabulary.

Resolve builtins lazily, after normal source declarations and local names.
The upstream parser and its type inference still process the complete input.
"""

from copy import copy

from m2isar import M2SyntaxError
from m2isar.frontends.coredsl2.behavior_model_builder import BehaviorModelBuilder
from m2isar.metamodel import arch, behav, type_info


class Seal5BehaviorModelBuilder(BehaviorModelBuilder):
    """Provide typed memory/register views and the branch procedure."""

    def visitReference_expression(self, ctx):
        name = ctx.ref.text
        scopes = (
            self._vars,
            self._fields,
            self._parameters,
            self._memory_aliases,
            self._memories,
            self._register_aliases,
            self._register_banks,
        )
        if any(name in scope for scope in scopes):
            return super().visitReference_expression(ctx)
        source, width = None, None
        if name in ("MEM8", "MEM16", "MEM32", "MEM64", "MEMX"):
            source = self._memories.get("MEM")
            if name == "MEMX":
                registers = self._register_banks.get("X")
                if registers is not None:
                    width = arch.get_const_or_val(registers.ty.element_type.size)
            else:
                width = int(name[3:])
        elif name == "XW":
            source = self._register_banks.get("X")
            if source is not None and arch.get_const_or_val(source.ty.element_type.size) == 64:
                width = 32
        if source is None or width is None:
            return super().visitReference_expression(ctx)
        view = copy(source)
        view.name = name
        view.ty = copy(source.ty)
        view.ty.element_type = type_info.PrimitiveType(type_info.TypeKind.UINT, width)
        # Cache views within this builder, but do not change the shared ISA.
        self._vars[name] = view
        return super().visitReference_expression(ctx)

    def visitProcedure_call(self, ctx):
        if ctx.ref.text == "branch" and "branch" not in self._functions:
            args = [self.visit(arg) for arg in ctx.args] if ctx.args else []
            if len(args) != 1:
                raise M2SyntaxError("branch expects exactly one condition argument")
            function = arch.Function(
                "branch",
                {},
                None,
                type_info.TypeKind.VOID,
                [arch.FnParam("condition", type_info.PrimitiveType(type_info.TypeKind.UINT, 1))],
                None,
                extern=True,
            )
            return behav.ProcedureCall(function, args)
        return super().visitProcedure_call(ctx)


def main():
    """Use the standard set parser with the Seal5 behavior builder."""
    from m2isar.frontends.coredsl2_set import parser
    from m2isar.transforms.infer_types import transform as inference
    from seal5.transform.infer_types.visitor import InferTypesMutator

    original = parser.BehaviorModelBuilder
    original_inference = inference.InferTypesMutator
    try:
        parser.BehaviorModelBuilder = Seal5BehaviorModelBuilder
        inference.InferTypesMutator = InferTypesMutator
        parser.main()
    finally:
        parser.BehaviorModelBuilder = original
        inference.InferTypesMutator = original_inference


if __name__ == "__main__":
    main()
