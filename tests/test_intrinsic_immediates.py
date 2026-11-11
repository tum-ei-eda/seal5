# SPDX-License-Identifier: Apache-2.0
"""Intrinsic signatures and matcher operands must agree with the declaration."""

from types import SimpleNamespace
import unittest

from seal5.backends.riscv_intrinsics.writer import build_attr
from seal5.backends.riscv_instr_info.writer import gen_intrinsic_pattern
from seal5.settings import ExtensionsSettings, IntrinsicDefn, IntrinsicArg


class IntrinsicImmediateTests(unittest.TestCase):
    def intrinsic(self):
        return IntrinsicDefn(
            instr_name="TEST",
            intrinsic_name="test",
            set_name="Test",
            ret_type="i32",
            args=[
                IntrinsicArg(arg_name="imm", arg_type="i32", immediate=True),
                IntrinsicArg(arg_name="rs1", arg_type="i32"),
            ],
        )

    def test_immediate_argument_is_verified_by_llvm(self):
        text = build_attr("test", self.intrinsic())
        self.assertIn("ImmArg<ArgIndex<0>>", text)
        self.assertNotIn("ImmArg<ArgIndex<1>>", text)

    def test_intrinsic_order_is_independent_of_assembly_order(self):
        instr = SimpleNamespace(
            name="TEST", llvm_intrin_reads=["GPR:$rs1", "timm:$imm"], llvm_intrin_ins_str="GPR:$rs1, timm:$imm"
        )
        text = gen_intrinsic_pattern(instr, "Test", self.intrinsic(), ExtensionsSettings(arch="xtest"))
        self.assertIn("(OpNode timm:$imm, GPR:$rs1), (Inst GPR:$rs1, timm:$imm)", text)


if __name__ == "__main__":
    unittest.main()
