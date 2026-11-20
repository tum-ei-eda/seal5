"""Generated branches match custom-lowered RISC-V DAGs, never the GI importer."""
import unittest
from seal5.tools.cdsl2llvm import lower_branch_patterns_to_riscv


class BranchDAGPatterns(unittest.TestCase):
    def pattern(self, cc):
        return ('def Helper : Instruction;\n'
                'def : Pat<(brcond (i32 (setcc (i32 (and GPR:$a, GPR:$b)), '
                '(i32 (i32 7)), '+cc+')), bb:$offset), (BR GPR:$a, GPR:$b, bb:$offset)>;\n')

    def test_all_predicates(self):
        for cc in ('SETEQ','SETNE','SETLT','SETGE','SETULT','SETUGE','SETGT','SETLE','SETUGT','SETULE'):
            with self.subTest(cc=cc):
                result=lower_branch_patterns_to_riscv(self.pattern(cc))
                self.assertNotIn('(brcond ',result)
                self.assertIn('(riscv_brcc ',result)
                self.assertTrue(result.startswith('def Helper : Instruction;\n'))
                self.assertEqual(result.count('GISelShouldIgnore'),1)
                self.assertEqual(lower_branch_patterns_to_riscv(result),result)

    def test_greater_than_swaps_operands(self):
        result=lower_branch_patterns_to_riscv(self.pattern('SETGT'))
        self.assertIn('(riscv_brcc (i32 (i32 7)), (i32 (and GPR:$a, GPR:$b)), SETLT, bb:$offset)',result)

    def test_unknown_condition_is_rejected(self):
        with self.assertRaises(ValueError):lower_branch_patterns_to_riscv(self.pattern('SETOEQ'))

    def test_rv64(self):
        result=lower_branch_patterns_to_riscv(self.pattern('SETNE').replace('i32','i64'))
        self.assertIn('(riscv_brcc (i64 (and',result)
