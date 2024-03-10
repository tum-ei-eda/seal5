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


class Seal5RegisterClass(IntEnum):
    GPR = 0
    FPR = 1
    CSR = 2
    CUSTOM = 3
    UNKNOWN = 4
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
