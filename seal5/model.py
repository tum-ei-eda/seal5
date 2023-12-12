# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich
"""TODO"""

from enum import IntEnum
from typing import List

from m2isar.metamodel.arch import InstructionSet, Instruction
from m2isar.metamodel.behav import Operation

class Seal5InstructionSet(InstructionSet):
	"""TODO."""

	def __init__(self, name: str, extension: "list[str]", constants: "dict[str, Constant]", memories: "dict[str, Memory]",
			functions: "dict[str, Function]", instructions: "dict[tuple[int, int], Instruction]", intrinsics: "dict[str, Seal5Intrinsic]", constraints: "dict[str, Seal5Constraint]", aliases: "dict[str, Seal5Alias]", registers: "dict[str, Seal5Register]", register_groups: "dict[str, Seal5RegisterGroup]"):
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
		return [Seal5Register(name, size=self.size, width=self.width, reg_class=self.reg_class) for  name in self.names]

	def __len__(self):
		return len(self.names)

	# TODO: allow indexing i.e. via group[12]


class Seal5Instruction(Instruction):

	def __init__(self, name, attributes: "dict[InstrAttribute, list[BaseNode]]", encoding: "list[Union[BitField, BitVal]]",
			mnemonic: str, assembly: str, operation: Operation, constraints: "list[Seal5Constraint]"):

		super().__init__(name, attributes, encoding, mnemonic, assembly, operation)
		self.constraints = constraints
