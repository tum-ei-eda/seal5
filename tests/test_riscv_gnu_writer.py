# SPDX-License-Identifier: Apache-2.0
"""Regression tests for GNU patch generation and fail-closed source checks."""

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from m2isar.metamodel.arch import BitVal

from seal5.backends.riscv_gnu.writer import collect, generate_patch
from seal5.model import Seal5RegOperand, Seal5RegisterClass, Seal5Type, DataType
from seal5.settings import ExtensionsSettings
from test_riscv_gnu_encoding import field


def model():
    operands = {
        name: Seal5RegOperand(name, Seal5Type(DataType.U, 5, 1), {}, [], Seal5RegisterClass.GPR)
        for name in ("rd", "rs1", "rs2")
    }
    instruction = SimpleNamespace(
        name="NAND",
        mnemonic="xunit.nand",
        encoding=[
            BitVal(7, 0x49),
            field("rs2", 4, 0),
            field("rs1", 4, 0),
            BitVal(3, 6),
            field("rd", 4, 0),
            BitVal(7, 0x2B),
        ],
        operands=operands,
        get_asm_str=lambda: "{name(rd)}, {name(rs1)}, {name(rs2)}",
    )
    instruction_set = SimpleNamespace(
        settings=ExtensionsSettings(arch="xunit"),
        instructions={"NAND": instruction},
        xlen=32,
    )
    return SimpleNamespace(sets={"Unit": instruction_set})


class WriterTests(unittest.TestCase):
    def test_table_preserves_operand_order_and_extension(self):
        header, opcodes, extensions, manifest = collect([model()])
        self.assertIn("Xseal50_,Xseal51_,Xseal52_", opcodes[0])
        self.assertIn("INSN_CLASS_SEAL5_XUNIT", opcodes[0])
        self.assertIn("0x9200602bULL, 0xfe00707fULL", opcodes[0])
        self.assertIn("{15, 0, 5}", header)
        self.assertEqual(extensions, {"xunit": "1.0"})
        self.assertEqual(manifest[0]["size"], 32)
        self.assertEqual(collect([model()]), collect([model()]))

    def test_compressed_registers(self):
        obj = model()
        instruction = obj.sets["Unit"].instructions["NAND"]
        instruction.operands["rd"].reg_class = Seal5RegisterClass.GPRC
        instruction.operands["rd"].ty.width = 3
        instruction.encoding[-2] = field("rd", 2, 0)
        instruction.encoding[-3] = BitVal(5, 6)
        instruction.get_asm_str = lambda: "{name(8+rd)}, {name(rs1)}, {name(rs2)}"
        header, _, _, _ = collect([obj])
        self.assertIn("{3, 3, 0, 1,", header)
        instruction.operands["rd"].ty.width = 4
        with self.assertRaisesRegex(ValueError, "3-bit index"):
            collect([obj])

    def test_unknown_register_class_rejected(self):
        obj = model()
        obj.sets["Unit"].instructions["NAND"].operands["rd"].reg_class = Seal5RegisterClass.UNKNOWN
        with self.assertRaisesRegex(ValueError, "Unsupported register class"):
            collect([obj])

    def test_duplicate_mnemonics_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate mnemonic"):
            collect([model(), model()])

    def test_ambiguous_instruction_length_rejected(self):
        obj = model()
        obj.sets["Unit"].instructions["NAND"].encoding[-1] = BitVal(7, 0x3F)
        with self.assertRaisesRegex(ValueError, "instruction length"):
            collect([obj])

    def test_unknown_assembly_expression_rejected(self):
        obj = model()
        obj.sets["Unit"].instructions["NAND"].get_asm_str = lambda: "{rd+1}, {rs1}, {rs2}"
        with self.assertRaisesRegex(ValueError, "assembly syntax"):
            collect([obj])

    def test_patch_has_all_components_and_does_not_mutate_source(self):
        sources = {
            "include/opcode/riscv.h": "enum riscv_insn_class {\n  INSN_CLASS_I,\n};\n",
            "opcodes/riscv-opc.c": "const struct riscv_opcode riscv_opcodes[] =\n{\n};\n",
            "opcodes/riscv-dis.c": '#include "opcode/riscv.h"\n' "print_insn_args () {\n switch (*oparg) {}\n}\n",
            "gas/config/tc-riscv.c": '#include "opcode/riscv.h"\n'
            "validate_riscv_insn () { switch (*oparg) {} }\n"
            "riscv_ip () { switch (*oparg) {} }\n",
            "bfd/elfxx-riscv.c": "static struct riscv_supported_ext riscv_supported_std_ext[] =\n{\n};\n"
            "riscv_multi_subset_supports () {\n    case INSN_CLASS_I:\n}\n",
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for path, content in sources.items():
                dest = root / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(content)
            patch, _ = generate_patch([model()], root)
            self.assertIn("--- /dev/null\n+++ b/include/opcode/riscv-seal5.h", patch)
            for path, content in sources.items():
                self.assertIn("+++ b/" + path, patch)
                self.assertEqual((root / path).read_text(), content)
            (root / "opcodes/riscv-opc.c").write_text("unsupported source layout\n")
            with self.assertRaisesRegex(ValueError, "source anchor"):
                generate_patch([model()], root)


if __name__ == "__main__":
    unittest.main()
