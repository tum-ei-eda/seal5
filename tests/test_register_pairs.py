# SPDX-License-Identifier: Apache-2.0
"""RV32 pair operands retain a single 64-bit physical register class."""
import unittest

from m2isar.metamodel import arch, behav, type_info
from seal5 import model
from seal5.transform.collect_register_operands.collect import VisitorContext
from seal5.transform.collect_register_operands.visitor import CollectRegisterOperandsVisitor
from seal5.backends.riscv_instr_info.writer import gen_intrinsic_pattern
from seal5.settings import ExtensionsSettings, IntrinsicDefn
from types import SimpleNamespace


class RegisterPairTests(unittest.TestCase):
    def collect(self, offset, pairs=("rs1",), width=32):
        kind = type_info.TypeKind.UINT
        registers = arch.RegisterBank("X", 32, kind, width, {})
        index = behav.NamedReference(arch.BitFieldDescr("rs1", 5, kind))
        if offset:
            index = behav.BinaryOperation(index, behav.Operator("+"), behav.Literal(offset))
        operand = model.Seal5Operand("rs1", model.Seal5Type(model.DataType.U, 5, 1), {}, [])
        context = VisitorContext({"rs1": operand}, pairs)
        CollectRegisterOperandsVisitor().generate(behav.IndexedReference(registers, index), context)
        return context.operands["rs1"]

    def test_both_words_use_the_same_pair_operand(self):
        for offset in (0, 1):
            with self.subTest(offset=offset):
                operand = self.collect(offset)
                self.assertEqual(operand.reg_class, model.Seal5RegisterClass.GPRPair)
                self.assertEqual(operand.reg_ty.width, 64)
                self.assertEqual(operand.attributes[model.Seal5OperandAttribute.REG_CLASS], "GPRPair")

    def test_ordinary_gprs_are_unchanged(self):
        operand = self.collect(0, pairs=())
        self.assertEqual(operand.reg_class, model.Seal5RegisterClass.GPR)
        self.assertEqual(operand.reg_ty.width, 32)
        with self.assertRaises(NotImplementedError):
            self.collect(1, pairs=())

    def test_invalid_pair_width_and_offset_are_rejected(self):
        for offset, width in ((2, 32), (0, 64)):
            with self.subTest(offset=offset, width=width), self.assertRaises(ValueError):
                self.collect(offset, width=width)

    def test_scalar_pair_intrinsic_does_not_emit_an_illegal_i64_pattern(self):
        instr = SimpleNamespace(llvm_writes=["GPRPair:$rd"])
        intrinsic = IntrinsicDefn(instr_name="PAIR_ADD64", intrinsic_name="add64", ret_type="i64")
        text = gen_intrinsic_pattern(instr, "XRegPairs", intrinsic, ExtensionsSettings(arch="xregpairs"))
        self.assertNotIn("Pat<", text)
        self.assertIn("custom RV32 type legalization", text)
