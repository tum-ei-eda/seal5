# SPDX-License-Identifier: Apache-2.0
"""Regression tests for CSR instruction operands."""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from seal5.backends.riscv_register_info.writer import gen_riscv_register_info_str
from seal5.model import (
    DataType,
    Seal5InstrAttribute,
    Seal5Instruction,
    Seal5OperandAttribute,
    Seal5RegOperand,
    Seal5Register,
    Seal5RegisterClass,
    Seal5RegisterGroup,
    Seal5Type,
)
from seal5.transform.check_pattern_support import check
from m2isar.metamodel import behav


class CSRSupportTests(unittest.TestCase):
    def run_pattern_support(self, instruction, registers, *flags):
        set_def = SimpleNamespace(
            name="Test",
            instructions={instruction.name: instruction},
            registers=registers,
        )
        model = SimpleNamespace(sets={"Test": set_def})
        args = check.get_parser().parse_args(["test.seal5model", *flags])
        with patch.object(check, "load_model", return_value=model), patch.object(check, "dump_model"):
            check.run(args)
        return Seal5InstrAttribute.SKIP_PATTERN_GEN not in instruction.attributes

    def test_csr_operand_uses_builtin_llvm_system_register_operand(self):
        instruction = object.__new__(Seal5Instruction)
        instruction.operands = {
            "csr": Seal5RegOperand(
                "csr",
                Seal5Type(DataType.U, 12, 1),
                {Seal5OperandAttribute.IN: []},
                [],
                Seal5RegisterClass.CSR,
            )
        }
        instruction._llvm_asm_str = "$csr"
        instruction._llvm_asm_order = ["$csr"]
        instruction._llvm_ins_str = None
        instruction.attributes = {}
        instruction.encoding = []

        instruction._llvm_process_operands()

        self.assertEqual(instruction.llvm_ins_str, "csr_sysreg:$csr")

    def test_only_implicitly_used_csr_registers_are_generated(self):
        registers = {
            "CSR0": Seal5Register("CSR0", 1, 32, False, False, Seal5RegisterClass.CSR),
            "CSR1": Seal5Register("CSR1", 1, 32, False, False, Seal5RegisterClass.CSR),
        }
        instruction_set = SimpleNamespace(
            registers=registers,
            register_groups={"CSR": Seal5RegisterGroup(["CSR0", "CSR1"], 1, 32, False, False, Seal5RegisterClass.CSR)},
            instructions={
                "read_csr": SimpleNamespace(
                    attributes={
                        Seal5InstrAttribute.USES: ["CSR0"],
                        Seal5InstrAttribute.DEFS: ["CSR1"],
                    }
                )
            },
        )

        self.assertEqual(
            gen_riscv_register_info_str(instruction_set),
            'let Namespace = "RISCV" in def CSR0 : Register<"csr0">;\n'
            'let Namespace = "RISCV" in def CSR1 : Register<"csr1">;',
        )

    def test_standalone_csr_register_is_generated_when_implicitly_used(self):
        instruction_set = SimpleNamespace(
            registers={"CSR": Seal5Register("CSR", 1, 32, False, False, Seal5RegisterClass.CSR)},
            register_groups={},
            instructions={
                "read_csr": SimpleNamespace(attributes={Seal5InstrAttribute.USES: ["CSR"]}),
            },
        )

        self.assertEqual(
            gen_riscv_register_info_str(instruction_set),
            'let Namespace = "RISCV" in def CSR : Register<"csr">;',
        )

    def test_csr_access_is_opt_in_for_pattern_generation(self):
        instruction = SimpleNamespace(
            name="read_csr",
            size=32,
            operands={
                "csr": SimpleNamespace(attributes={Seal5OperandAttribute.IN: []}),
                "rd": SimpleNamespace(attributes={Seal5OperandAttribute.OUT: []}),
            },
            attributes={
                Seal5InstrAttribute.USES: ["CSR0"],
                Seal5InstrAttribute.DEFS: ["CSR0"],
            },
            operation=behav.Operation([behav.Literal(1)]),
        )
        self.assertTrue(
            self.run_pattern_support(
                instruction, {"CSR0": SimpleNamespace(reg_class=Seal5RegisterClass.CSR)}, "--allow-csr"
            )
        )

    def test_csr_access_remains_opt_in(self):
        instruction = SimpleNamespace(
            name="read_csr",
            size=32,
            operands={
                "csr": SimpleNamespace(attributes={Seal5OperandAttribute.IN: []}),
                "rd": SimpleNamespace(attributes={Seal5OperandAttribute.OUT: []}),
            },
            attributes={Seal5InstrAttribute.USES: ["CSR0"]},
            operation=behav.Operation([behav.Literal(1)]),
        )

        self.assertFalse(
            self.run_pattern_support(instruction, {"CSR0": SimpleNamespace(reg_class=Seal5RegisterClass.CSR)})
        )

    def test_csr_write_without_explicit_result_is_supported(self):
        instruction = SimpleNamespace(
            name="write_csr",
            size=32,
            operands={"csr": SimpleNamespace(attributes={Seal5OperandAttribute.IN: []})},
            attributes={Seal5InstrAttribute.DEFS: ["CSR0"]},
            operation=behav.Operation([behav.Literal(1)]),
        )

        self.assertTrue(
            self.run_pattern_support(
                instruction, {"CSR0": SimpleNamespace(reg_class=Seal5RegisterClass.CSR)}, "--allow-csr"
            )
        )

    def test_csr_operand_allows_pattern_generation_without_result(self):
        instruction = SimpleNamespace(
            name="write_csr",
            size=32,
            operands={
                "csr": SimpleNamespace(
                    attributes={
                        Seal5OperandAttribute.IN: [],
                        Seal5OperandAttribute.REG_CLASS: Seal5RegisterClass.CSR.name,
                    }
                )
            },
            attributes={},
            operation=behav.Operation([behav.Literal(1)]),
        )

        self.assertTrue(self.run_pattern_support(instruction, {}, "--allow-csr"))

    def test_other_implicit_registers_remain_unsupported_with_csr_opt_in(self):
        instruction = SimpleNamespace(
            name="read_custom",
            size=32,
            operands={
                "rs1": SimpleNamespace(attributes={Seal5OperandAttribute.IN: []}),
                "rd": SimpleNamespace(attributes={Seal5OperandAttribute.OUT: []}),
            },
            attributes={Seal5InstrAttribute.USES: ["CUSTOM0"]},
            operation=behav.Operation([behav.Literal(1)]),
        )
        self.assertFalse(
            self.run_pattern_support(
                instruction, {"CUSTOM0": SimpleNamespace(reg_class=Seal5RegisterClass.CUSTOM)}, "--allow-csr"
            )
        )


if __name__ == "__main__":
    unittest.main()
