# SPDX-License-Identifier: Apache-2.0
"""Import packed support completely while retaining the legacy scalar path."""
from pathlib import Path
import tempfile
import unittest

from seal5.tools.cdsl2llvm import get_pattern_gen_backend_patch


class PackedSIMDImportTests(unittest.TestCase):
    def materialize(self, root, packed):
        source, native = root / "source", root / "native"
        target = Path("llvm/lib/Target/RISCV")
        files = [
            "GISel/RISCVInstructionSelector.cpp",
            "RISCVInstrInfo.cpp",
            "RISCVLateBranchOpt.cpp",
            "RISCVRedundantCopyElimination.cpp",
            "GISel/RISCVLegalizerInfo.cpp",
            "RISCVInstrInfo.td",
            "RISCVISelLowering.cpp",
            "RISCVTargetTransformInfo.cpp",
            "RISCVTargetTransformInfo.h",
            "RISCVRegisterInfo.cpp",
            "GISel/RISCVRegisterBankInfo.cpp",
            "GISel/RISCVRegisterBanks.td",
            "Disassembler/RISCVDisassembler.cpp",
            "RISCVRegisterInfo.td",
            "RISCVFeatures.td",
        ]
        for name in files:
            for tree, text in ((source, "SOURCE_SUPPORT\n"), (native, "NATIVE_SUPPORT\n")):
                path = tree / target / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text)
        (native / target / "GISel/RISCVLegalizerInfo.cpp").write_text(
            "NATIVE_LEGALIZER\n  case Intrinsic::riscv_vsetvli:\n"
        )
        (source / target / "RISCVInstrInfo.td").write_text(
            'include "/tmp/validation-only.td"\n'
            "def patterngen_btarget : Operand {\n}\n"
            "// PATTERNGEN_GPR32V_BRIDGES_BEGIN\nPACKED_BRIDGE\n// PATTERNGEN_GPR32V_BRIDGES_END\n"
        )
        if packed:
            (source / target / "RISCVRegisterInfo.td").write_text(
                'def GPR32V2 : RegisterClass<"RISCV", [v2i16], 32, (add X0)> {\n}\n'
                'def GPR32V4 : RegisterClass<"RISCV", [v4i8], 32, (add X0)> {\n}\n'
            )
            (source / target / "RISCVFeatures.td").write_text(
                'def FeatureGPR32V : SubtargetFeature<"gpr32v", "HasGPR32V", "true", "Packed">;\n'
                'def HasGPR32V : Predicate<"Subtarget->hasGPR32V()">;\n\n'
            )
        patch = get_pattern_gen_backend_patch(source, native, root)
        return Path(patch.file).read_text()

    def test_packed_import_contains_all_support(self):
        with tempfile.TemporaryDirectory() as folder:
            patch = self.materialize(Path(folder), True)
            for name in (
                "RISCVRegisterInfo.td",
                "RISCVFeatures.td",
                "RISCVISelLowering.cpp",
                "GISel/RISCVRegisterBanks.td",
                "GISel/RISCVRegisterBankInfo.cpp",
            ):
                self.assertIn("b/llvm/lib/Target/RISCV/" + name, patch)
            self.assertIn("+def GPR32V2", patch)
            self.assertIn("+def GPR32V4", patch)
            self.assertIn("+def FeatureGPR32V", patch)
            self.assertIn("+PACKED_BRIDGE", patch)
            self.assertNotIn("validation-only", patch)
            self.assertIn("+SOURCE_SUPPORT", patch)

    def test_legacy_keeps_native_legalizer(self):
        with tempfile.TemporaryDirectory() as folder:
            patch = self.materialize(Path(folder), False)
            self.assertIn("NATIVE_LEGALIZER", patch)
            self.assertIn("+  case Intrinsic::riscv_pg_branch:", patch)
            self.assertNotIn("b/llvm/lib/Target/RISCV/RISCVRegisterInfo.td", patch)
            self.assertNotIn("PACKED_BRIDGE", patch)


if __name__ == "__main__":
    unittest.main()
