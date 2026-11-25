import unittest
from seal5.tools.cdsl2llvm import ignore_gisel_patterns
from seal5.tools.cdsl2llvm import scalarize_test_inputs


class MemoryDAGPatternsTest(unittest.TestCase):
    def test_only_patterns_are_ignored(self):
        text='def Load : Instruction;\n  def : Pat<(load GPR:$a), (Load GPR:$a)>;\n'
        result=ignore_gisel_patterns(text)
        self.assertTrue(result.startswith('def Load : Instruction;'))
        self.assertIn('  let GISelShouldIgnore = 1 in def : Pat<',result)
        self.assertEqual(ignore_gisel_patterns(result),result)

    def test_register_operands_have_no_competing_memory_loads(self):
        source=('define i32 @implTEST(ptr readonly %rs1, ptr readonly %rs2) {\n'
                '  %rs1.v = load i32, ptr %rs1, align 4\n'
                '  %rs2.v = load i32, ptr %rs2, align 4\n'
                '  %p = inttoptr i32 %rs1.v to ptr\n'
                '  %v = load i8, ptr %p, align 1\n'
                '  %wide = sext i8 %v to i32\n'
                '  %sum = add i32 %wide, %rs2.v\n  ret i32 %sum\n}\n')
        result=scalarize_test_inputs(source)
        self.assertIn('@implTEST(i32 %rs1, i32 %rs2)',result)
        self.assertNotIn('load i32',result)
        self.assertNotIn('%rs1.v',result)
        self.assertIn('load i8, ptr %p',result)
        self.assertIn('add i32 %wide, %rs2',result)

    def test_input_output_pointer_survives_scalarization(self):
        source = """define void @implACC(ptr %rd, ptr readonly %rs1) {
  %old = load i32, ptr %rd, align 4
  %value = load i32, ptr %rs1, align 4
  %sum = add i32 %old, %value
  store i32 %sum, ptr %rd, align 4
  ret void
}
"""
        result = scalarize_test_inputs(source)
        self.assertIn("@implACC(ptr %rd, i32 %rs1)", result)
        self.assertIn("%old = load i32, ptr %rd", result)
        self.assertIn("store i32 %sum, ptr %rd", result)
        self.assertIn("add i32 %old, %rs1", result)

    def test_other_pointer_uses_survive_scalarization(self):
        source = """define ptr @implALIAS(ptr %rs1) {
  %value = load i32, ptr %rs1, align 4
  ret ptr %rs1
}
"""
        self.assertEqual(scalarize_test_inputs(source), source)
