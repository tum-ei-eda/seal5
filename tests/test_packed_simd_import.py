# SPDX-License-Identifier: Apache-2.0
"""Import packed support completely while retaining the legacy scalar path."""
from pathlib import Path
import tempfile
import difflib
import subprocess
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
        (native / target / "RISCVRegisterInfo.td").write_text(
            "NATIVE_SUPPORT\nlet RegInfos = XLenRI in {\n  NATIVE_REGISTER_TAIL\n}\n"
        )
        (native / target / "RISCVFeatures.td").write_text(
            'NATIVE_SUPPORT\ndef FeatureStdExtSvinval : RISCVExtension<1, 0, "Page-Based Memory Types">;\n'
            "NATIVE_FEATURE_TAIL\nNATIVE_FEATURE_TAIL2\nNATIVE_FEATURE_TAIL3\n\n"
        )
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
                'def FeatureGPR32VAdd : SubtargetFeature<"gpr32v-add", "HasGPR32VAdd", "true", "Add">;\n\n'
                'def FeatureGPR32VSub : SubtargetFeature<"gpr32v-sub", "HasGPR32VSub", "true", "Sub">;\n\n'
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

    def test_backend_import_preserves_marker_patch_context(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.materialize(root, True)
            native = root / "native"
            target = Path("llvm/lib/Target/RISCV")
            marker_diff = []
            for name in ("RISCVFeatures.td", "RISCVRegisterInfo.td"):
                path = target / name
                original = (native / path).read_text()
                # The LLVM 22 feature marker patch removes the last blank line;
                # the register marker patch adds its site at the end of file.
                updated = original[:-1] if name == "RISCVFeatures.td" else original + "\n// INSERTION_START\n"
                marker_diff.extend(
                    difflib.unified_diff(
                        original.splitlines(keepends=True),
                        updated.splitlines(keepends=True),
                        fromfile=f"a/{path}",
                        tofile=f"b/{path}",
                    )
                )
            marker_patch = root / "markers.patch"
            marker_patch.write_text("".join(marker_diff))
            for patch in (root / "pattern_gen_backend_support.patch", marker_patch):
                subprocess.run(["git", "apply", str(patch)], cwd=native, check=True, capture_output=True)
            self.assertIn("def GPR32V2", (native / target / "RISCVRegisterInfo.td").read_text())
            self.assertTrue((native / target / "RISCVRegisterInfo.td").read_text().endswith("// INSERTION_START\n"))
            self.assertIn("def FeatureGPR32V", (native / target / "RISCVFeatures.td").read_text())

    def test_capabilities_precede_generated_extension_site(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.materialize(root, True)
            native = root / "native"
            subprocess.run(
                ["git", "apply", str(root / "pattern_gen_backend_support.patch")],
                cwd=native,
                check=True,
                capture_output=True,
            )
            text = (native / "llvm/lib/Target/RISCV/RISCVFeatures.td").read_text()
            site = text.index("def FeatureStdExtSvinval")
            for name in ("FeatureGPR32V", "HasGPR32V", "FeatureGPR32VAdd", "FeatureGPR32VSub"):
                self.assertLess(text.index("def " + name + " "), site)

    def test_packed_legalizer_marker_whitespace(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.materialize(root, True)
            target = Path("llvm/lib/Target/RISCV/GISel/RISCVLegalizerInfo.cpp")
            content = (
                "  const LLT nxv8p0 = LLT::scalable_vector(8, p0);\n"
                "  const LLT nxv16p0 = LLT::scalable_vector(16, p0);\n\n"
                "  using namespace TargetOpcode;\n\n"
                "  auto BoolVecTys = {};\n"
            )
            (root / "native" / target).write_text(content)
            (root / "source" / target).write_text(content.replace("\n\n", "\n\n\n"))
            patch = get_pattern_gen_backend_patch(root / "source", root / "native", root)
            # Only whitespace at marker sites differs, so no legalizer diff remains.
            self.assertNotIn("b/" + str(target), Path(patch.file).read_text())

    def test_legacy_keeps_native_legalizer(self):
        with tempfile.TemporaryDirectory() as folder:
            patch = self.materialize(Path(folder), False)
            self.assertIn("NATIVE_LEGALIZER", patch)
            self.assertIn("+  case Intrinsic::riscv_pg_branch:", patch)
            self.assertNotIn("b/llvm/lib/Target/RISCV/RISCVRegisterInfo.td", patch)
            self.assertNotIn("PACKED_BRIDGE", patch)


if __name__ == "__main__":
    unittest.main()
