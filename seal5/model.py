# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich
"""TODO"""

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
    BitField,
    BitVal,
    DataType,
    SizedRefOrConst,
)
from m2isar.metamodel.behav import Operation, BinaryOperation, Operator, NamedReference, IntLiteral, SliceOperation


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


class Seal5RegisterClass(IntEnum):
    GPR = 0
    FPR = 1
    CSR = 2
    CUSTOM = 3


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

    def __init__(self, stmts):
        self.stmts = stmts


class Seal5Alias:
    pass


class Seal5InstrAttribute(Enum):
    HAS_SIDE_EFFECTS = auto()
    MAY_LOAD = auto()
    MAY_STORE = auto()
    IS_TERMINATOR = auto()
    IS_BRANCH = auto()


class Seal5OperandAttribute(Enum):
    IN = auto()  # or: READ (R)
    OUT = auto()  # or: WRITE (W)
    INOUT = auto()  # or: READWRITE (RW)
    UNUSED = auto()
    LANES = auto()
    IS_REG = auto()
    IS_IMM = auto()


class Seal5DataType(Enum):
    pass


class Seal5Type:
    datatype: Union[DataType, Seal5DataType] = DataType.NONE
    width: Optional[int] = None
    lanes: Optional[int] = None
    # TODO: is_vector,...

    def __init__(self, datatype, width, lanes):
        self.datatype = datatype
        self.width = width
        self.lanes = lanes


class Seal5Operand:
    name: str
    ty: Seal5Type
    attributes: Dict[Seal5OperandAttribute, List[BaseNode]] = {}
    constraints: List[Seal5Constraint] = []
    # TODO: track imm, const?
    # TODO: helpers (is_float, is_int,...)

    def __init__(self, name, ty, attributes, constraints):
        self.name = name
        self.ty = ty
        self.attributes = attributes
        self.constraints = constraints
        if self.ty.lanes is not None and Seal5OperandAttribute.LANES not in self.attributes:
            lanes = int(self.ty.lanes)
            self.attributes[Seal5OperandAttribute.LANES] = lanes
        if self.name in ["rd", "rs1", "rs2", "rs3"] and Seal5OperandAttribute.IS_REG not in self.attributes:
            self.attributes[Seal5OperandAttribute.IS_REG] = []
        if "imm" in self.name and Seal5OperandAttribute.IS_IMM not in self.attributes:
            self.attributes[Seal5OperandAttribute.IS_IMM] = []
        # TODO: shorter with op.is_imm,...
        if Seal5OperandAttribute.IS_IMM in self.attributes and (Seal5OperandAttribute.OUT in self.attributes or Seal5OperandAttribute.INOUT in self.attributes):
            raise RuntimeError("Imm operands can not be outputs!")


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
        print("name", name)
        self.constraints = constraints
        self.operands = {}
        for field_name, field in self.fields.items():
            if field_name in self.operands:
                continue
            width = field.size
            datatype = field.data_type
            lanes = None
            ty = Seal5Type(width=width, datatype=datatype, lanes=lanes)
            op_attrs = {Seal5OperandAttribute.IN: []}
            # check for fixed bits
            temp = [False] * width
            print("field_name", field_name)
            print("temp", temp)
            for enc in self.encoding:
                if isinstance(enc, BitField):
                    if enc.name == field_name:
                        print("enc", enc, dir(enc))
                        rng = enc.range
                        print("rng", rng)
                        assert rng.lower <= rng.upper
                        for pos in range(rng.lower, rng.upper + 1):
                            print("pos", pos)
                            assert pos < len(temp)
                            temp[pos] = True
            print("temp", temp)
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
            print("temp", temp)
            # input("pp")
            constraints = []
            for pos in temp:
                lower, upper = pos.split(":", 1)
                lower = int(lower)
                upper = int(upper)
                sz = upper - lower + 1
                stmt = BinaryOperation(SliceOperation(NamedReference(SizedRefOrConst(field_name, sz)), IntLiteral(upper), IntLiteral(lower)), Operator("=="), IntLiteral(0))
                constraint = Seal5Constraint([stmt])
                constraints.append(constraint)
            print("constraints", constraints)
            if len(constraints) > 0:
                # input("eee")
                pass
            op = Seal5Operand(field_name, ty, op_attrs, constraints)
            self.operands[field_name] = op
        # Test:
        # self.attributes[Seal5InstrAttribute.MAY_LOAD] = []
