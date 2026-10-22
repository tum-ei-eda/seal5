# SPDX-License-Identifier: Apache-2.0
"""Translate Seal5 instruction encodings without assuming standard RISC-V fields."""

from dataclasses import dataclass

from m2isar.metamodel.arch import BitField, BitVal


@dataclass(frozen=True)
class Slice:
    """One contiguous piece of an operand in the instruction word."""

    instruction_bit: int
    operand_bit: int
    width: int


@dataclass(frozen=True)
class Encoding:
    """Fixed bits and operand slices, shared by GNU code generators."""

    size: int
    match: int
    mask: int
    operands: dict

    def extract(self, word, name, signed=False, width=None):
        """Decode split operands, including implicit zero low bits."""
        value = 0
        slices = self.operands[name]
        for part in slices:
            value |= ((word >> part.instruction_bit) & ((1 << part.width) - 1)) << part.operand_bit
        if signed:
            if width is None:
                width = max(part.operand_bit + part.width for part in slices)
            if value & (1 << (width - 1)):
                value -= 1 << width
        return value

    def insert(self, values):
        """Encode numeric operands, rejecting truncation and missing operands."""
        if set(values) != set(self.operands):
            raise ValueError("Operand names must match the encoding")
        word = self.match
        for name, slices in self.operands.items():
            value = values[name]
            bits = sum(((1 << part.width) - 1) << part.operand_bit for part in slices)
            width = bits.bit_length()
            if value < -(1 << (width - 1)) or value > bits:
                raise ValueError(f"Operand {name} does not fit its encoding")
            unsigned = value & ((1 << width) - 1)
            if unsigned & ~bits:
                raise ValueError(f"Operand {name} has nonzero implicit bits")
            for part in slices:
                word |= ((unsigned >> part.operand_bit) & ((1 << part.width) - 1)) << part.instruction_bit
        return word


def compile_encoding(instruction):
    """Compile CoreDSL's MSB-first encoding into bit positions used by GNU."""
    position = 0
    match = 0
    mask = 0
    operands = {}
    for field in reversed(instruction.encoding):
        if isinstance(field, BitVal):
            width = field.length
            if field.value < 0 or field.value >= 1 << width:
                raise ValueError(f"Invalid fixed encoding in {instruction.name}")
            match |= field.value << position
            mask |= ((1 << width) - 1) << position
        elif isinstance(field, BitField):
            width = field.range.length
            part = Slice(position, field.range.lower, width)
            previous = operands.setdefault(field.name, [])
            used = ((1 << width) - 1) << part.operand_bit
            if any(used & (((1 << item.width) - 1) << item.operand_bit) for item in previous):
                raise ValueError(f"Overlapping operand bits in {instruction.name}: {field.name}")
            previous.append(part)
        else:
            raise TypeError(f"Unsupported encoding field: {type(field).__name__}")
        if width <= 0:
            raise ValueError(f"Empty encoding field in {instruction.name}")
        position += width
    if position not in (16, 32, 48, 64):
        raise ValueError(f"Unsupported instruction size for {instruction.name}: {position}")
    return Encoding(position, match, mask, {name: tuple(parts) for name, parts in operands.items()})
