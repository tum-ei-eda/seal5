// Test the SubIncAcc instruction of the TUM "example" extension.
// After calling the function the value 10 should be present in
// register a0, where an integer return value would be expected
//
// Compile with the "example" extension specified:
//   clang test_subincacc.c -c --target=riscv32 -march=rv32ixexample
// then disassembly shows the new instruction:
//   llvm-objdump -d test_subincacc.o --disassembler-options=numeric

__attribute__((naked)) void test_subincacc() {
    asm("li a0, 11");
    asm("li a1, 5");
    asm("li a2, 7");
    asm("cv_subincacc a0, a1, a2");
}
