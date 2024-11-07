# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

from antlr4 import ParserRuleContext

from m2isar import M2DuplicateError
from .parser_gen import CoreDSL2Parser, CoreDSL2Visitor


class CoreContainerContext(ParserRuleContext):
    pass


class LoadOrder(CoreDSL2Visitor):
    def __init__(self) -> None:
        super().__init__()
        self.instruction_sets: "dict[str, CoreDSL2Parser.Instruction_setContext]" = {}
        # self.core_defs = {}
        self.stacks = {}

    def visitInstruction_set(self, ctx: CoreDSL2Parser.Instruction_setContext):
        name = ctx.name.text
        # print("set", name, [e.text for e in ctx.extension])

        if name in self.instruction_sets:
            raise M2DuplicateError(f"instruction set {name} specified more than once")

        self.instruction_sets[name] = ctx
        stack = []
        for e in ctx.extension:
            assert e.text in self.stacks, f"Set not found: {e.text}. Missing include?"
            for x in self.stacks[e.text]:
                if x not in stack:
                    stack.append(x)
            stack.append(e.text)
        self.stacks[name] = stack
        # print("stacks", self.stacks)

    # def extend_ins_set(self, ins_set_name):
    # 	if ins_set_name not in self.instruction_sets:
    # 		raise M2NameError(f"instruction set {ins_set_name} is unknown")

    # 	extensions = [e.text for e in self.instruction_sets[ins_set_name].extension]
    # 	if extensions:
    # 		ret = [ins_set_name]
    # 		for extension in extensions:
    # 			ret = self.extend_ins_set(extension) + ret
    # 		return ret
    # 	else:
    # 		return [ins_set_name]

    # def visitCore_def(self, ctx: CoreDSL2Parser.Core_defContext):
    # 	name = ctx.name.text
    # 	contributing_types = [c.text for c in ctx.contributing_types]

    # 	ins_set_queue = []
    # 	known_sets = set()

    # 	for ct in contributing_types:
    # 		new_sets = self.extend_ins_set(ct)
    # 		for new_set in new_sets:
    # 			if new_set not in known_sets:
    # 				known_sets.add(new_set)
    # 				ins_set_queue.append(self.instruction_sets[new_set])

    # 	ins_set_queue.append(ctx)
    # 	self.core_defs[name] = ins_set_queue

    def visit(self, tree):
        # print("visit", tree)
        _ = super().visit(tree)

        ret = {}

        # for core_name, contents in self.core_defs.items():
        # 	container = CoreContainerContext()
        # 	container.children = contents
        # 	container.name = core_name
        # 	ret[core_name] = container
        for set_name, set_def in self.instruction_sets.items():
            container = CoreContainerContext()
            container.children = [self.instruction_sets[x] for x in self.stacks[set_name]] + [set_def]
            container.name = set_name
            ret[set_name] = container

        return ret
