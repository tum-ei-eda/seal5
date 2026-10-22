"""Tests for GNU encoding translation (run with unittest discovery)."""

import unittest
from types import SimpleNamespace

from m2isar.metamodel.arch import BitField, BitVal, RangeSpec
from m2isar.metamodel.type_info import TypeKind

from seal5.backends.riscv_gnu.encoding import compile_encoding


def field(name, upper, lower):
    return BitField(name, RangeSpec(upper, lower), TypeKind.UINT)


class EncodingTests(unittest.TestCase):
    def test_r_type_known_word(self):
        instruction = SimpleNamespace(
            name="nand",
            encoding=[
                BitVal(7, 0x49),
                field("rs2", 4, 0),
                field("rs1", 4, 0),
                BitVal(3, 6),
                field("rd", 4, 0),
                BitVal(7, 0x2B),
            ],
        )
        encoding = compile_encoding(instruction)
        self.assertEqual(encoding.match, 0x9200602B)
        self.assertEqual(encoding.mask, 0xFE00707F)
        word = encoding.insert({"rd": 10, "rs1": 11, "rs2": 12})
        self.assertEqual(word, 0x92C5E52B)
        self.assertEqual(encoding.extract(word, "rs1"), 11)
        with self.assertRaises(ValueError):
            encoding.insert({"rd": 32, "rs1": 0, "rs2": 0})

    def test_split_signed_branch_immediate(self):
        instruction = SimpleNamespace(
            name="branch",
            encoding=[
                field("imm", 12, 12),
                field("imm", 10, 5),
                field("rs2", 4, 0),
                field("rs1", 4, 0),
                BitVal(3, 0),
                field("imm", 4, 1),
                field("imm", 11, 11),
                BitVal(7, 0x63),
            ],
        )
        encoding = compile_encoding(instruction)
        # beq zero, zero, -4
        self.assertEqual(encoding.insert({"imm": -4, "rs1": 0, "rs2": 0}), 0xFE000EE3)
        self.assertEqual(encoding.extract(0xFE000EE3, "imm", signed=True), -4)
        with self.assertRaises(ValueError):
            encoding.insert({"imm": 3, "rs1": 0, "rs2": 0})

    def test_overlapping_source_bits_rejected(self):
        instruction = SimpleNamespace(
            name="invalid",
            encoding=[
                field("imm", 4, 0),
                field("imm", 4, 0),
                BitVal(6, 0),
            ],
        )
        with self.assertRaisesRegex(ValueError, "Overlapping"):
            compile_encoding(instruction)


if __name__ == "__main__":
    unittest.main()
