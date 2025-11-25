# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

import itertools
from typing import Union

from m2isar import M2DuplicateError, M2NameError, M2TypeError, M2ValueError, flatten
from m2isar.metamodel import arch, behav, intrinsics
from .parser_gen import CoreDSL2Parser, CoreDSL2Visitor
from .utils import RADIX, SHORTHANDS, SIGNEDNESS

from seal5.logging import Logger

logger = Logger("frontends.arch_builder")


class ArchitectureModelBuilder(CoreDSL2Visitor):
    """ANTLR visitor to build an M2-ISA-R architecture model of a CoreDSL 2 specification."""

    _constants: "dict[str, arch.Constant]"
    _instructions: "dict[str, arch.Instruction]"
    _functions: "dict[str, arch.Function]"
    _always_blocks: "dict[str, arch.AlwaysBlock]"
    _instruction_sets: "dict[str, arch.InstructionSet]"
    _read_types: "dict[str, str]"
    _memories: "dict[str, arch.Memory]"
    _memory_aliases: "dict[str, arch.Memory]"
    _overwritten_instrs: "list[tuple[arch.Instruction, arch.Instruction]]"
    _instr_classes: "set[int]"
    _main_reg_file: Union[arch.Memory, None]

    def __init__(self):
        super().__init__()
        self._constants = {}
        self._instructions = {}
        self._functions = {}
        self._always_blocks = {}
        self._instruction_sets = {}
        self._read_types = {}
        self._memories = {}
        self._memory_aliases = {}

        self._overwritten_instrs = []
        self._instr_classes = set()
        self._main_reg_file = None

    def visitBit_field(self, ctx: CoreDSL2Parser.Bit_fieldContext):
        """Generate a bit field (instruction parameter in encoding)."""

        # generate lower and upper bounds
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)

        # instantiate M2-ISA-R objects
        range = arch.RangeSpec(left.value, right.value)
        return arch.BitField(ctx.name.text, range, arch.DataType.U)

    def visitBit_value(self, ctx: CoreDSL2Parser.Bit_valueContext):
        """Generate a fixed encoding part."""

        val = self.visit(ctx.value)
        return arch.BitVal(val.bit_size, val.value)

    def visitInstruction_set(self, ctx: CoreDSL2Parser.Instruction_setContext):
        """Generate a top-level instruction set object."""
        # print("visitInstruction_set", ctx.name.text)
        # print("len(self._constants) 1", len(self._constants))
        # input("22")

        # keep track of seen instruction set names
        self._read_types[ctx.name.text] = None

        name = ctx.name.text
        extension = []
        if ctx.extension:
            extension = [obj.text for obj in ctx.extension]

        # generate flat list of instruction set contents
        contents = flatten([self.visit(obj) for obj in ctx.sections])
        # print("len(self._constants) 2", len(self._constants))
        # input("33")

        constants = {}
        constants.update(self._constants)
        memories = {}
        memories.update(self._memories)
        functions = {}
        functions.update(self._functions)
        instructions = {}
        # instructions.update(self._instructions)

        # group contents by type
        for item in contents:
            if isinstance(item, arch.Constant):
                constants[item.name] = item
            elif isinstance(item, arch.Memory):
                memories[item.name] = item
            elif isinstance(item, arch.Function):
                functions[item.name] = item
                item.ext_name = name
            elif isinstance(item, arch.Instruction):
                instructions[(item.code, item.mask)] = item
                item.ext_name = name
            elif isinstance(item, arch.AlwaysBlock):
                pass
            else:
                raise M2ValueError("unexpected item encountered")

        # instantiate M2-ISA-R object
        i = arch.InstructionSet(name, extension, constants, memories, functions, instructions)

        if name in self._instruction_sets:
            raise M2DuplicateError(f'instruction set "{name}" already defined')

        # keep track of instruction set object
        self._instruction_sets[name] = i
        return i

    def visitSection_instructions(self, ctx: CoreDSL2Parser.Section_instructionsContext):
        attributes = dict([self.visit(obj) for obj in ctx.attributes])
        instructions: "list[arch.Instruction]" = [self.visit(obj) for obj in ctx.instructions]

        for attr, val in attributes.items():
            for instr in instructions:
                if attr not in instr.attributes:
                    instr.attributes[attr] = val

        return instructions

    def visitCore_def(self, ctx: CoreDSL2Parser.Core_defContext):
        """Generate a top-level CoreDef object."""

        self.visitChildren(ctx)

        name = ctx.name.text

        c = arch.CoreDef(
            name,
            list(self._read_types.keys()),
            None,
            self._constants,
            self._memories,
            self._memory_aliases,
            self._functions,
            self._instructions,
            self._instr_classes,
            intrinsics,
        )

        return c

    def visitSection_arch_state(self, ctx: CoreDSL2Parser.Section_arch_stateContext):
        """Generate "archictectural_state" section of CoreDSL file."""

        decls = [self.visit(obj) for obj in ctx.declarations]
        decls = list(itertools.chain.from_iterable(decls))
        for obj in ctx.expressions:
            self.visit(obj)

        return decls

    def visitAlways_block(self, ctx: CoreDSL2Parser.Always_blockContext):
        """Generate always block"""

        name = ctx.name.text
        attributes = dict([self.visit(obj) for obj in ctx.attributes])

        a = arch.AlwaysBlock(name, attributes, ctx.behavior)

        self._always_blocks[name] = a

        return a

    def visitInstruction(self, ctx: CoreDSL2Parser.InstructionContext):
        """Generate non-behavioral parts of an instruction."""

        # read encoding, attributes and disassembly
        encoding = [self.visit(obj) for obj in ctx.encoding]
        attributes = dict([self.visit(obj) for obj in ctx.attributes])
        assembly = ctx.assembly.text.replace('"', "") if ctx.assembly is not None else None
        mnemonic = ctx.mnemonic.text.replace('"', "") if ctx.mnemonic is not None else None

        i = arch.Instruction(ctx.name.text, attributes, encoding, mnemonic, assembly, ctx.behavior, None)
        self._instr_classes.add(i.size)

        instr_id = (i.code, i.mask)

        # check for duplicate instructions
        if instr_id in self._instructions:
            self._overwritten_instrs.append((self._instructions[instr_id], i))

        # keep track of instruction
        self._instructions[instr_id] = i

        return i

    def visitFunction_definition(self, ctx: CoreDSL2Parser.Function_definitionContext):
        """Generate non-behavioral parts of a function."""

        # decode attributes
        attributes = dict([self.visit(obj) for obj in ctx.attributes])

        if arch.FunctionAttribute.ETISS_TRAP_ENTRY_FN in attributes:
            attributes[arch.FunctionAttribute.ETISS_NEEDS_ARCH] = []

        # decode return type and name
        type_ = self.visit(ctx.type_)
        name = ctx.name.text

        # decode function arguments
        params = []
        if ctx.params:
            params = self.visit(ctx.params)

        if not isinstance(params, list):
            params = [params]

        return_size = None
        data_type = arch.DataType.NONE

        if isinstance(type_, arch.IntegerType):
            return_size = type_._width
            data_type = arch.DataType.S if type_.signed else arch.DataType.U

        f = arch.Function(name, attributes, return_size, data_type, params, ctx.behavior, ctx.extern is not None)

        # error on duplicate function definition
        # TODO: implement overwriting function prototypes?
        f2 = self._functions.get(name, None)

        if f2 is not None:
            if len(f2.operation.statements) > 0:
                raise M2DuplicateError(f'function "{name}" already defined')

            self._functions.pop(name)

        self._functions[name] = f
        return f

    def visitParameter_declaration(self, ctx: CoreDSL2Parser.Parameter_declarationContext):
        """Generate function argument declaration."""

        # type is required, name and array size optional
        type_ = self.visit(ctx.type_)
        name = None
        # size = None
        if ctx.decl:
            if ctx.decl.name:
                name = ctx.decl.name.text
            if ctx.decl.size:
                ctx.decl.size = [self.visit(obj) for obj in ctx.decl.size]

        p = arch.FnParam(name, type_._width, arch.DataType.S if type_.signed else arch.DataType.U)
        return p

    def visitInteger_constant(self, ctx: CoreDSL2Parser.Integer_constantContext):
        """Generate an integer literal."""

        # extract raw text
        text: str = ctx.value.text.lower()

        # extract tick position for verilog-stlye literal
        tick_pos = text.find("'")

        # decode verilog-style literal
        if tick_pos != -1:
            width = int(text[:tick_pos])
            radix = text[tick_pos + 1]
            value = int(text[tick_pos + 2 :], RADIX[radix])

        # decode normal dec, hex, bin, oct literal
        # TODO: remove width inference from text
        else:
            value = int(text, 0)
            if text.startswith("0b"):
                width = len(text) - 2
            elif text.startswith("0x"):
                width = (len(text) - 2) * 4
            elif text.startswith("0") and len(text) > 1:
                width = (len(text) - 1) * 3
            else:
                width = value.bit_length()

        return behav.IntLiteral(value, width)

    def visitDeclaration(self, ctx: CoreDSL2Parser.DeclarationContext):
        """Generate a declaration."""

        # extract storage type, qualifiers and attributes
        storage = [self.visit(obj) for obj in ctx.storage]
        # qualifiers = [self.visit(obj) for obj in ctx.qualifiers]
        attributes = dict([self.visit(obj) for obj in ctx.attributes])

        # extract data type
        type_ = self.visit(ctx.type_)

        # extract list of contained declarations for the given type
        decls: "list[CoreDSL2Parser.DeclaratorContext]" = ctx.declarations

        ret_decls = []

        # generate each declaration
        for decl in decls:
            name = decl.name.text

            # generate a register alias
            if type_.ptr == "&":
                # error out on duplicate declaration
                if name in self._memory_aliases:
                    raise M2DuplicateError(f"memory {name} already defined")

                # assume default size
                size = [1]
                # alias needs to have a reference as initializer
                init: behav.IndexedReference = self.visit(decl.init)
                attributes = {}

                # extract array size
                if decl.size:
                    size = [self.visit(obj).value for obj in decl.size]

                # extract referenced object and indices
                left = init.index
                right = init.right if init.right is not None else left
                reference = init.reference

                if decl.attributes:
                    attributes = dict([self.visit(obj) for obj in decl.attributes])

                range = arch.RangeSpec(left, right)

                # if range.length != size[0]:
                # 	raise ValueError(f"range mismatch for \"{name}\"")

                # instantiate M2-ISA-R object, keep track of parent - child relations
                m = arch.Memory(name, range, type_._width, attributes)
                m.parent = reference
                m.parent.children.append(m)

                # keep track of this declaration globally
                self._memory_aliases[name] = m
                # keep track of this declaration for this declaration statement
                ret_decls.append(m)

            # normal declaration
            else:
                # no storage specifier -> implementation parameter, "Constant" in M2-ISA-R
                if len(storage) == 0:
                    if name in self._constants:
                        raise M2DuplicateError(f"constant {name} already defined")

                    # extract initializer if present
                    init = None
                    if decl.init is not None:
                        init = self.visit(decl.init)

                    c = arch.Constant(name, init, [], type_._width, type_.signed)

                    self._constants[name] = c
                    ret_decls.append(c)

                # register and extern declaration: "Memory" object in M2-ISA-R
                elif "register" in storage or "extern" in storage:
                    if name in self._memories:
                        raise M2DuplicateError(f"memory {name} already defined")

                    size = [1]
                    init = None
                    attributes = {}

                    if decl.size:
                        size = [self.visit(obj) for obj in decl.size]

                    if len(size) > 1:
                        raise NotImplementedError("arrays with more than one dimension are not supported")

                    if decl.init is not None:
                        init = self.visit(decl.init)

                    if decl.attributes:
                        attributes = dict([self.visit(obj) for obj in decl.attributes])

                    range = arch.RangeSpec(size[0])
                    m = arch.Memory(name, range, type_._width, attributes)

                    # attach init value to memory object
                    if init is not None:
                        m._initval[None] = init.generate(None)

                    if arch.MemoryAttribute.IS_MAIN_REG in attributes:
                        self._main_reg_file = m

                    self._memories[name] = m
                    ret_decls.append(m)

        return ret_decls

    def visitType_specifier(self, ctx: CoreDSL2Parser.Type_specifierContext):
        type_ = self.visit(ctx.type_)
        if ctx.ptr:
            type_.ptr = ctx.ptr.text
        return type_

    def visitInteger_type(self, ctx: CoreDSL2Parser.Integer_typeContext):
        """Generate an integer type specification."""

        # default signedness
        signed = True
        # minimal integer type is just a signedness without width
        width = None

        # extract sign
        if ctx.signed is not None:
            signed = self.visit(ctx.signed)

        # extract size
        if ctx.size is not None:
            width = self.visit(ctx.size)

        # extract and decode shorthand (int = signed<32>)
        if ctx.shorthand is not None:
            width = self.visit(ctx.shorthand)

        # type check width
        if isinstance(width, behav.IntLiteral):
            width = width.value
        elif isinstance(width, behav.NamedReference):
            width = width.reference
        else:
            raise M2TypeError("width has wrong type")

        return arch.IntegerType(width, signed, None)

    def visitVoid_type(self, ctx: CoreDSL2Parser.Void_typeContext):
        """Generate a void type."""
        return arch.VoidType(None)

    def visitBool_type(self, ctx: CoreDSL2Parser.Bool_typeContext):
        """Generate a bool (alias for unsigned<1>)."""
        return arch.IntegerType(1, False, None)

    def visitBinary_expression(self, ctx: CoreDSL2Parser.Binary_expressionContext):
        """Generate a binary expression."""

        # visit LHS and RHS
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        op = behav.Operator(ctx.bop.text)

        # return M2-ISA-R object
        return behav.BinaryOperation(left, op, right)

    def visitSlice_expression(self, ctx: CoreDSL2Parser.Slice_expressionContext):
        left = self.visit(ctx.left)
        right = self.visit(ctx.right) if ctx.right is not None else None
        expr = self.visit(ctx.expr).reference

        op = behav.IndexedReference(expr, left, right)
        return op

    def visitPrefix_expression(self, ctx: CoreDSL2Parser.Prefix_expressionContext):
        prefix = behav.Operator(ctx.prefix.text)
        expr = self.visit(ctx.right)
        return behav.UnaryOperation(prefix, expr)

    def visitReference_expression(self, ctx: CoreDSL2Parser.Reference_expressionContext):
        """Generate a referencing expression."""

        name = ctx.ref.text

        # try to resolve the reference, error out if invalid
        ref = self._constants.get(name) or self._memories.get(name) or self._memory_aliases.get(name)
        if ref is None:
            raise M2NameError(f'reference "{name}" could not be resolved')
        return behav.NamedReference(ref)

    def visitStorage_class_specifier(self, ctx: CoreDSL2Parser.Storage_class_specifierContext):
        return ctx.children[0].symbol.text

    def visitType_qualifier(self, ctx: CoreDSL2Parser.Type_qualifierContext):
        return ctx.children[0].symbol.text

    def visitInteger_signedness(self, ctx: CoreDSL2Parser.Integer_signednessContext):
        return SIGNEDNESS[ctx.children[0].symbol.text]

    def visitInteger_shorthand(self, ctx: CoreDSL2Parser.Integer_shorthandContext):
        return behav.IntLiteral(SHORTHANDS[ctx.children[0].symbol.text])

    def visitAssignment_expression(self, ctx: CoreDSL2Parser.Assignment_expressionContext):
        """Generate an assignment."""

        # extract LHS and RHS
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)

        # if LHS is a reference, assign RHS as its default value
        if isinstance(left, behav.NamedReference):
            if isinstance(left.reference, arch.Constant):
                left.reference.value = right.generate(None)

            elif isinstance(left.reference, arch.Memory):
                left.reference._initval[None] = right.generate(None)

        elif isinstance(left, behav.IndexedReference):
            left.reference._initval[left.index.generate(None)] = right.generate(None)

    def visitAttribute(self, ctx: CoreDSL2Parser.AttributeContext):
        """Generate an attribute."""

        name = ctx.name.text

        # read attribute from enums
        attr = (
            arch.InstrAttribute._member_map_.get(name.upper())
            or arch.MemoryAttribute._member_map_.get(name.upper())
            or arch.FunctionAttribute._member_map_.get(name.upper())
        )

        # warn if attribute is unknown to M2-ISA-R
        if attr is None:
            logger.warning('unknown attribute "%s" encountered', name)
            attr = name

        return attr, ctx.params

    def visitChildren(self, node):
        """Helper method to return flatter results on tree visits."""
        # print("visitChildren", node)

        ret = super().visitChildren(node)
        if isinstance(ret, list) and len(ret) == 1:
            return ret[0]
        return ret

    def aggregateResult(self, aggregate, nextResult):
        """Aggregate results from multiple children into a list."""

        ret = aggregate
        if nextResult is not None:
            if ret is None:
                ret = [nextResult]
            else:
                ret += [nextResult]
        return ret
