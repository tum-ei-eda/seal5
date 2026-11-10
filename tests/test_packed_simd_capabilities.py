# SPDX-License-Identifier: Apache-2.0
"""ISA capabilities must follow the generated extension, not representation alone."""
import unittest

from seal5.backends.riscv_features.writer import gen_riscv_features_str
from seal5.settings import ExtensionsSettings, LLVMSettings, LLVMState, LLVMVersion


class PackedSIMDCapabilityTests(unittest.TestCase):
    def generate(self, features):
        extension = ExtensionsSettings(
            feature="XPackedSIMD32",
            predicate="StdExtXPackedSIMD32",
            arch="xpackedsimd32",
            version="1.0",
            backend_features=features,
        )
        llvm = LLVMSettings(state=LLVMState(version=LLVMVersion(major=22, minor=1, patch=8)))
        return gen_riscv_features_str("XPackedSIMD32", extension, llvm, {}, False)[0]

    def test_explicit_non_isa_capabilities(self):
        content = self.generate(["FeatureGPR32VSub", "FeatureGPR32VAdd", "FeatureGPR32VAdd"])
        self.assertIn("[FeatureGPR32VAdd, FeatureGPR32VSub]", content)
        self.assertIn("RISCVExtension<", content)

    def test_scalar_extension_has_no_packed_capabilities(self):
        self.assertNotIn("FeatureGPR32V", self.generate(None))

    def test_invalid_record_name(self):
        with self.assertRaises(AssertionError):
            self.generate(["gpr32v-add"])


if __name__ == "__main__":
    unittest.main()
