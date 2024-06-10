# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich
"""TODO"""

import re
from enum import IntEnum, Enum, auto
from typing import Dict, List, Optional, Union

from m2isar.metamodel.arch import (
    InstructionSet,
    Instruction,
    Constant,
    Memory,
    Function,
    BaseNode,
    InstrAttribute,
    MemoryAttribute,
    BitField,
    BitVal,
    DataType,
    SizedRefOrConst,
)
from m2isar.metamodel.behav import Operation, BinaryOperation, Operator, NamedReference, IntLiteral, SliceOperation

from seal5.settings import ExtensionsSettings


class Seal5InstructionSet(InstructionSet):
    """TODO."""

    def __init__(
        self,
        name: str,
        extension: "list[str]",
        constants: "dict[str, Constant]",
        memories: "dict[str, Memory]",
        functions: "dict[str, Function]",
        instructions: "dict[tuple[int, int], Instruction]",
        intrinsics: "dict[str, Seal5Intrinsic]",
        constraints: "dict[str, Seal5Constraint]",
        aliases: "dict[str, Seal5Alias]",
        registers: "dict[str, Seal5Register]",
        register_groups: "dict[str, Seal5RegisterGroup]",
    ):
        super().__init__(name, extension, constants, memories, functions, instructions)

        self.intrinsics = intrinsics
        self.constraints = constraints
        self.aliases = aliases
        self.registers = registers
        self.register_groups = register_groups
        self.settings: ExtensionsSettings = None
        self._xlen = None

    @property
    def xlen(self):
        if self._xlen is None:
            for mem_name, mem_def in self.memories.items():
                if mem_name == "X" or MemoryAttribute.IS_MAIN_REG in mem_def.attributes:
                    self._xlen = mem_def.size
                    break
        assert self._xlen is not None, "Could not determine XLEN"
        return self._xlen


class Seal5RegisterClass(IntEnum):
    GPR = 0
    FPR = 1
    CSR = 2
    CUSTOM = 3
    UNKNOWN = 4
    GPRC = 5
    # TODO: use auto()
    # TODO: GPRv2, GPRv4 // GPR32V2, GPR32V4


class Seal5Register:
    def __init__(self, name: str, size: int, width: int, reg_class: Seal5RegisterClass):
        self.name = name
        self.size = size
        self.width = width
        self.reg_class = reg_class


class Seal5RegisterGroup:
    def __init__(self, names: List[str], size: int, width: int, reg_class: Seal5RegisterClass):
        self.names = names
        self.size = size
        self.width = width
        self.reg_class = reg_class

    @property
    def registers(self):
        return [Seal5Register(name, size=self.size, width=self.width, reg_class=self.reg_class) for name in self.names]

    def __len__(self):
        return len(self.names)

    # TODO: allow indexing i.e. via group[12]


class Seal5Intrinsic:
    pass


class Seal5Constraint:
    stmts: List[BaseNode]
    description: Optional[str] = None

    def __init__(self, stmts, description=None):
        self.stmts = stmts
        self.description = description


class Seal5Alias:
    pass


class Seal5InstrAttribute(Enum):
    HAS_SIDE_EFFECTS = auto()
    MAY_LOAD = auto()
    MAY_STORE = auto()
    IS_TERMINATOR = auto()
    IS_BRANCH = auto()
    COMPRESSED = auto()


class Seal5OperandAttribute(Enum):
    IN = auto()  # or: READ (R)
    OUT = auto()  # or: WRITE (W)
    INOUT = auto()  # or: READWRITE (RW)
    UNUSED = auto()
    # LANES = auto()
    IS_REG = auto()
    IS_IMM = auto()
    TYPE = auto()
    REG_CLASS = auto()
    REG_TYPE = auto()


class Seal5DataType(Enum):
    pass


# class Seal5OperandClass(Enum):
#     UNKNOWN = auto()
#     REG = auto()
#     IMM = auto()


class Seal5Type:
    datatype: Union[DataType, Seal5DataType] = DataType.NONE
    width: Optional[int] = None
    lanes: Optional[int] = None
    # TODO: is_vector,...

    def __init__(self, datatype, width, lanes):
        self.datatype = datatype
        self.width = width
        self.lanes = lanes

    def __repr__(self):
        sign_letter = None
        if self.datatype == DataType.U:
            sign_letter = "u"
        elif self.datatype == DataType.S:
            sign_letter = "s"
        assert sign_letter is not None
        if self.lanes is None:
            lanes = 1
        else:
            lanes = self.lanes
        if self.width is None:
            width_ = "?"
        else:
            assert self.width % lanes == 0
            width_ = self.width // lanes
        ret = f"{sign_letter}{width_}"
        if lanes > 1:
            ret = f"v{lanes}{ret}"
        return ret


class Seal5Operand:
    name: str
    ty: Seal5Type
    _attributes: Dict[Seal5OperandAttribute, List[BaseNode]] = {}
    constraints: List[Seal5Constraint] = []
    # TODO: track imm, const?
    # TODO: helpers (is_float, is_int,...)

    def __repr__(self):
        return f"{type(self)}({self.name}, ty={self.ty}, attrs={self.attributes})"

    @property
    def attributes(self):
        ret = self._attributes
        if self.ty is not None:
            # if Seal5OperandAttribute.LANES not in ret:
            #     lanes = int(self.ty.lanes)
            #     ret[Seal5OperandAttribute.LANES] = lanes
            ret[Seal5OperandAttribute.TYPE] = str(self.ty)
        return ret

    def __init__(self, name, ty, attributes, constraints):
        self.name = name
        self.ty = ty
        self._attributes = attributes
        self.constraints = constraints


class Seal5ImmOperand(Seal5Operand):
    def __init__(self, name, ty, attributes, constraints):
        super().__init__(name, ty, attributes, constraints)
        if Seal5OperandAttribute.IS_IMM not in self.attributes:
            self.attributes[Seal5OperandAttribute.IS_IMM] = []
        if Seal5OperandAttribute.OUT in self.attributes or Seal5OperandAttribute.INOUT in self.attributes:
            raise RuntimeError("Imm operands can not be outputs!")

    @property
    def attributes(self):
        ret = super().attributes
        if Seal5OperandAttribute.IS_IMM not in ret:
            ret[Seal5OperandAttribute.IS_IMM] = []
        return ret


class Seal5RegOperand(Seal5Operand):
    reg_class: Seal5RegisterClass
    reg_ty: Seal5Type

    def __init__(self, name, ty, attributes, constraints, reg_class=Seal5RegisterClass.UNKNOWN, reg_ty=None):
        super().__init__(name, ty, attributes, constraints)
        self.reg_class = reg_class
        self.reg_ty = reg_ty

    @property
    def attributes(self):
        ret = super().attributes
        if Seal5OperandAttribute.IS_REG not in ret:
            ret[Seal5OperandAttribute.IS_REG] = []
        if Seal5OperandAttribute.REG_CLASS not in ret:
            ret[Seal5OperandAttribute.REG_CLASS] = self.reg_class.name
        if Seal5OperandAttribute.REG_TYPE not in ret:
            ret[Seal5OperandAttribute.REG_TYPE] = str(self.reg_ty)
        return ret


class Seal5GPROperand(Seal5RegOperand):
    def __init__(self, name, ty, attributes, constraints, reg_ty):
        super().__init__(name, ty, attributes, constraints, Seal5RegisterClass.GPR, reg_ty)


class Seal5FPROperand(Seal5RegOperand):
    def __init__(self, name, ty, attributes, constraints, reg_ty):
        super().__init__(name, ty, attributes, constraints, Seal5RegisterClass.FPR, reg_ty)


class Seal5CSROperand(Seal5RegOperand):
    def __init__(self, name, ty, attributes, constraints, reg_ty):
        super().__init__(name, ty, attributes, constraints, Seal5RegisterClass.CSR, reg_ty)


class Seal5Instruction(Instruction):
    def __init__(
        self,
        name,
        attributes: Dict[Union[InstrAttribute, Seal5InstrAttribute], List[BaseNode]],
        encoding: "list[Union[BitField, BitVal]]",
        mnemonic: str,
        assembly: str,
        operation: Operation,
        constraints: "list[Seal5Constraint]",
        operands: "dict[str, Seal5Operand]",
    ):
        super().__init__(name, attributes, encoding, mnemonic, assembly, operation)
        # print("name", name)
        self.constraints = constraints
        self.operands = {}
        self._llvm_asm_str = None
        self._llvm_asm_order = None
        self._llvm_constraints = None
        self._llvm_reads = None
        self._llvm_writes = None
        self._llvm_ins_str = None
        self._llvm_outs_str = None
        self._process_fields()

    def _process_fields(self):
        for field_name, field in self.fields.items():
            if field_name in self.operands:
                continue
            width = field.size
            datatype = field.data_type
            lanes = None
            ty = Seal5Type(width=width, datatype=datatype, lanes=lanes)
            # op_attrs = {Seal5OperandAttribute.IN: []}
            op_attrs = {}
            # check for fixed bits
            temp = [False] * width
            # print("field_name", field_name)
            # print("temp", temp)
            for enc in self.encoding:
                if isinstance(enc, BitField):
                    if enc.name == field_name:
                        # print("enc", enc, dir(enc))
                        rng = enc.range
                        # print("rng", rng)
                        assert rng.lower <= rng.upper
                        for pos in range(rng.lower, rng.upper + 1):
                            # print("pos", pos)
                            assert pos < len(temp)
                            temp[pos] = True
            # print("temp", temp)
            temp = [pos for pos, val in enumerate(temp) if not val]
            temp2 = []
            cur = None
            for pos in temp:
                if cur is None:
                    cur = [pos, pos]
                else:
                    if pos == cur[1] + 1:
                        cur[1] = pos
                    else:
                        temp2.append(f"{cur[0]}:{cur[1]}")
                        cur = [pos, pos]
            if cur is not None:
                temp2.append(f"{cur[0]}:{cur[1]}")
            temp = temp2
            # print("temp", temp)
            # input("pp")
            constraints = []
            for pos in temp:
                lower, upper = pos.split(":", 1)
                lower = int(lower)
                upper = int(upper)
                sz = upper - lower + 1
                stmt = BinaryOperation(
                    SliceOperation(
                        NamedReference(SizedRefOrConst(field_name, sz)), IntLiteral(upper), IntLiteral(lower)
                    ),
                    Operator("=="),
                    IntLiteral(0),
                )
                constraint = Seal5Constraint([stmt])
                constraints.append(constraint)
            # print("constraints", constraints)
            if len(constraints) > 0:
                # input("eee")
                pass
            # if "imm" in field_name:
            #     cls = Seal5ImmOperand
            # elif field_name in ["rd", "rs1", "rs2", "rs3"]:
            #     cls = Seal5RegOperand
            cls = Seal5Operand
            op = cls(field_name, ty, op_attrs, constraints)
            self.operands[field_name] = op
        # Test:
        # self.attributes[Seal5InstrAttribute.MAY_LOAD] = []

    def _llvm_check_operands(self):
        asm_order = self.llvm_asm_order
        operands = self.operands
        # check that number of operands is equal
        assert len(asm_order) == len(operands), "Number of operands does not match (asm vs. CDSL)"
        # check that order of operands matches asm syntax
        # for op_idx, op_name in enumerate(operands.keys()):
        #     asm_idx = asm_order.index(f"${op_name}")
        #     assert asm_idx == op_idx, "Order of asm operands does not match CDSL operands"

    def _llvm_process_operands(self):
        operands = self.operands
        reads = []
        writes = []
        constraints = []
        self._llvm_check_operands()
        for op_name, op in operands.items():
            if len(op.constraints) > 0:
                raise NotImplementedError
            if Seal5OperandAttribute.IS_REG in op.attributes:
                assert Seal5OperandAttribute.REG_CLASS in op.attributes
                cls = op.attributes[Seal5OperandAttribute.REG_CLASS]
                assert cls in ["GPR", "GPRC"]
                pre = cls
            elif Seal5OperandAttribute.IS_IMM in op.attributes:
                assert Seal5OperandAttribute.TYPE in op.attributes
                ty = op.attributes[Seal5OperandAttribute.TYPE]
                assert ty[0] in ["u", "s"]
                sz = int(ty[1:])
                pre = f"{ty[0]}imm{sz}"

            if Seal5OperandAttribute.INOUT in op.attributes or (
                Seal5OperandAttribute.OUT in op.attributes and Seal5OperandAttribute.IN in op.attributes
            ):
                op_str2 = f"{pre}:${op_name}_wb"
                writes.append(op_str2)
                op_str = f"{pre}:${op_name}"
                reads.append(op_str)
                constraint = f"${op_name} = ${op_name}_wb"
                constraints.append(constraint)

            elif Seal5OperandAttribute.OUT in op.attributes:
                op_str = f"{pre}:${op_name}"
                writes.append(op_str)
            elif Seal5OperandAttribute.IN in op.attributes:
                op_str = f"{pre}:${op_name}"
                reads.append(op_str)
        self._llvm_constraints = constraints
        self._llvm_reads = reads
        self._llvm_writes = writes

    def _llvm_process_assembly(self):
        asm_str = self.assembly
        asm_str = re.sub(r"name\(([a-zA-Z0-9_\+]+)\)", r"\g<1>", asm_str)
        asm_str = re.sub(r"{([a-zA-Z0-9_\+]+):[#0-9a-zA-Z\._]+}", r"{\g<1>}", asm_str)
        asm_str = re.sub(r"{([a-zA-Z0-9_\+]+)}", r"$\g<1>", asm_str)
        # remove offsets
        asm_str = re.sub(r"[0-9]+\+([a-zA-Z0-9]+)", r"\g<1>", asm_str)
        asm_str = re.sub(r"([a-zA-Z0-9]+)\+[0-9]+", r"\g<1>", asm_str)
        asm_order = re.compile(r"(\$[a-zA-Z0-9_]+)").findall(asm_str)
        for op in asm_order:
            if f"{op}(" in asm_str or f"{op})" in asm_str or f"{op}!" in asm_str or f"!{op}" in asm_str:
                asm_str = asm_str.replace(op, "${" + op[1:] + "}")
        self._llvm_asm_str = asm_str
        self._llvm_asm_order = asm_order

    @property
    def llvm_asm_str(self):
        if self._llvm_asm_str is None:
            self._llvm_process_assembly()
        return self._llvm_asm_str

    @property
    def llvm_asm_order(self):
        if self._llvm_asm_order is None:
            self._llvm_process_assembly()
        return self._llvm_asm_order

    @property
    def llvm_constraints(self):
        if self._llvm_constraints is None:
            self._llvm_process_operands()
        return self._llvm_constraints

    @property
    def llvm_reads(self):
        if self._llvm_reads is None:
            self._llvm_process_operands()
        return self._llvm_reads

    @property
    def llvm_writes(self):
        if self._llvm_writes is None:
            self._llvm_process_operands()
        return self._llvm_writes

    @property
    def llvm_ins_str(self):
        if self._llvm_ins_str is None:
            reads = self.llvm_reads
            reads_ = [(x.split(":", 1)[1] if ":" in x else x) for x in reads]
            ins_str = ", ".join([reads[reads_.index(x)] for x in self._llvm_asm_order if x in reads_])
            if len(ins_str) == 0:
                assert len(reads) == 0
            self._llvm_ins_str = ins_str
        return self._llvm_ins_str

    @property
    def llvm_outs_str(self):
        if self._llvm_outs_str is None:
            writes = self.llvm_writes
            writes_ = [(x.split(":", 1)[1] if ":" in x else x).replace("_wb", "") for x in writes]
            outs_str = ", ".join([writes[writes_.index(x)] for x in self._llvm_asm_order if x in writes_])
            if len(outs_str) == 0:
                assert len(writes) == 0
            self._llvm_outs_str = outs_str
        return self._llvm_outs_str

    @property
    def llvm_attributes(self):
        attrs = {}
        if Seal5InstrAttribute.HAS_SIDE_EFFECTS in self.attributes:
            attrs["hasSideEffects"] = 1
        else:
            attrs["hasSideEffects"] = 0
        if Seal5InstrAttribute.MAY_LOAD in self.attributes:
            attrs["mayLoad"] = 1
        else:
            attrs["mayLoad"] = 0
        if Seal5InstrAttribute.MAY_STORE in self.attributes:
            attrs["mayStore"] = 1
        else:
            attrs["mayStore"] = 0
        if Seal5InstrAttribute.IS_TERMINATOR in self.attributes:
            attrs["isTerminator"] = 1
        else:
            attrs["isTerminator"] = 0
        return attrs

    def llvm_get_compressed_pat(self, set_def):
        # TODO: map metamodel instr names to llvm instr names
        uncompressed_instr = self.attributes.get(Seal5InstrAttribute.COMPRESSED, None)
        if uncompressed_instr is None or len(uncompressed_instr) == 0:
            return None
        if isinstance(uncompressed_instr, list):
            uncompressed_instr = uncompressed_instr[0]
        compressed_instr = self.name
        print("compressed_instr", compressed_instr)
        uncompressed_instr = uncompressed_instr.value.strip()
        print("uncompressed_instr", uncompressed_instr)
        uncompressed = None
        assert set_def is not None
        for _, instr_def in set_def.instructions.items():
            print("idn", instr_def.name)
            if instr_def.name == uncompressed_instr:
                print("if")
                uncompressed = instr_def
                print("break")
                break
        assert uncompressed is not None, f"Could not find instr {uncompressed_instr} in set {set_def.name}"
        print("uncompressed", uncompressed)
        print("compressed_constraints", self.llvm_constraints)
        print("compressed_ins_str", self.llvm_ins_str)
        print("compressed_outs_str", self.llvm_outs_str)
        print("compressed_asm_order", self.llvm_asm_order)
        print("uncompressed_constraints", uncompressed.llvm_constraints)
        print("uncompressed_ins_str", uncompressed.llvm_ins_str)
        print("uncompressed_outs_str", uncompressed.llvm_outs_str)
        print("uncompressed_asm_order", uncompressed.llvm_asm_order)
        # TODO: rs1_wb vs. rd_wb?
        uncompressed_asm_order_ = None
        assert len(uncompressed.llvm_constraints) == 0
        if len(self.llvm_asm_order) == len(uncompressed.llvm_asm_order):
            print("EQUAL")
            raise NotImplementedError
        elif len(self.llvm_asm_order) < len(uncompressed.llvm_asm_order):
            print("LESS")
            assert len(self.llvm_asm_order) == (len(uncompressed.llvm_asm_order) - 1)
            missing = set(uncompressed.llvm_asm_order) - set(self.llvm_asm_order)
            assert len(missing) == 1
            missing = list(missing)[0]
            print("missing", missing)
            assert len(self.llvm_constraints) > 0
            wb_reg = None
            for constr in self.llvm_constraints:
                print("constr", constr)
                m = re.compile(r"(\$[a-zA-Z0-9]*)\s*=\s*(\$[a-zA-Z0-9]*)_wb").match(constr)
                if m:
                    x, y = m.groups()
                    if x == y:
                        wb_reg = x
            print("wb_reg", wb_reg)

            def replace_helper(x):
                if x == missing:
                    return wb_reg
                # if x == wb_reg:
                #     return f"{wb_reg}_wb"
                return x

            uncompressed_asm_order_ = [replace_helper(x) for x in uncompressed.llvm_asm_order]
            print("uncompressed_asm_order", uncompressed_asm_order_)
        else:
            raise RuntimeError("Compressed instr has more args than uncompressed one")
        assert uncompressed_asm_order_ is not None
        # compressed_args = "GPRC:$rs1, GPRC:$rs2"

        def args_helper(asm_order, ins_str, outs_str):
            ret = []
            for x in asm_order:
                for y in outs_str.split(", ") + ins_str.split(", "):
                    y_ = y.split(":", 1)[-1]
                    if y_ == x:
                        ret.append(y)
                        break
            assert len(ret) == len(asm_order)
            return ", ".join(ret)

        compressed_args = args_helper(self.llvm_asm_order, self.llvm_ins_str, self.llvm_outs_str)
        print("compressed_args", compressed_args)
        uncompressed_args = args_helper(uncompressed_asm_order_, self.llvm_ins_str, self.llvm_outs_str)
        # uncompressed_args = "GPRC:$rs1, GPRC:$rs1, GPRC:$rs2"
        print("uncompressed_args", uncompressed_args)
        uncompressed_str = f"{uncompressed_instr} {uncompressed_args}"
        print("uncompressed_str", uncompressed_str)
        compressed_str = f"{compressed_instr} {compressed_args}"
        print("compressed_str", compressed_str)
        ret = f"def : CompressPat<({uncompressed_str}), ({compressed_str})>;"
        print("ret", ret)

        # raise NotImplementedError
        return ret
