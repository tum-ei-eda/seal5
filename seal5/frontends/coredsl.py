# SPDX-License-Identifier: Apache-2.0
"""CoreDSL set frontend accepting the explicit pattern-gen vocabulary.

Resolve builtins lazily, after normal source declarations and local names.
The upstream parser and its type inference still process the complete input.
"""

from copy import copy
import ast

from antlr4 import Token
from m2isar import M2SyntaxError
from m2isar.frontends.coredsl2.behavior_model_builder import BehaviorModelBuilder
from m2isar.frontends.coredsl2.architecture_model_builder import ArchitectureModelBuilder
from m2isar.metamodel import arch, behav, type_info


def make_set_attribute_parser(filename, make_parser, set_attributes):
    """Parse set header attributes using the upstream attribute grammar."""
    parser = make_parser(filename)
    stream = parser.getTokenStream()
    stream.fill()
    tokens = stream.tokens
    depth = 0
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if depth == 0 and token.text == "InstructionSet" and i + 2 < len(tokens):
            name = tokens[i + 1]
            j = i + 2
            if tokens[j].text == "extends" and j + 2 < len(tokens):
                j += 2
                while tokens[j].text == "," and j + 2 < len(tokens):
                    j += 2
            attributes = {}
            while tokens[j].text == "[[":
                stream.seek(j)
                attr = parser.attribute()
                end = stream.index
                key = attr.name.text.lower()
                if key in attributes:
                    raise M2SyntaxError(f"duplicate attribute {key} on instruction set {name.text}")
                if len(attr.params) > 1:
                    raise M2SyntaxError(f"attribute {key} on instruction set {name.text} expects at most one value")
                value = attr.params[0].getText() if attr.params else None
                if value and value[0] in ("'", '"'):
                    value = ast.literal_eval(value)
                attributes[key] = value
                for item in tokens[j:end]:
                    item.channel = Token.HIDDEN_CHANNEL
                j = end
            if attributes:
                set_attributes[id(name)] = attributes
                i = j - 1
        if token.text == "{":
            depth += 1
        elif token.text == "}":
            depth -= 1
        i += 1
    stream.seek(0)
    return parser


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
    from m2isar.frontends.coredsl2 import importer
    from m2isar.transforms.infer_types import transform as inference
    from seal5.transform.infer_types.visitor import InferTypesMutator

    set_attributes = {}
    original_make_parser = parser.make_parser
    original_import_parser = importer.make_parser
    original_architecture = parser.ArchitectureModelBuilder

    class Seal5ArchitectureModelBuilder(ArchitectureModelBuilder):
        def visitInstruction_set(self, ctx):
            result = super().visitInstruction_set(ctx)
            result.attributes = set_attributes.get(id(ctx.name), {})
            return result

    original = parser.BehaviorModelBuilder
    original_inference = inference.InferTypesMutator
    try:
        parser.make_parser = lambda filename: make_set_attribute_parser(filename, original_make_parser, set_attributes)
        importer.make_parser = lambda filename: make_set_attribute_parser(
            filename, original_import_parser, set_attributes
        )
        parser.ArchitectureModelBuilder = Seal5ArchitectureModelBuilder
        parser.BehaviorModelBuilder = Seal5BehaviorModelBuilder
        inference.InferTypesMutator = InferTypesMutator
        parser.main()
    finally:
        parser.make_parser = original_make_parser
        importer.make_parser = original_import_parser
        parser.ArchitectureModelBuilder = original_architecture
        parser.BehaviorModelBuilder = original
        inference.InferTypesMutator = original_inference


if __name__ == "__main__":
    main()
