# RUN: not llvm-mc -triple=riscv32 -mattr=+xregpairs %s 2>&1 | FileCheck %s
pair.add64 x11, x12, x14
# CHECK: error: {{.*}}even{{.*}}
pair.add64 x10, x13, x14
# CHECK: error: {{.*}}even{{.*}}
pair.add64 x10, x12, x15
# CHECK: error: {{.*}}even{{.*}}
pair.add.2x32 x31, x12, x14
# CHECK: error: {{.*}}even{{.*}}
pair.add64 x10, x12
# CHECK: error:
pair.add64 x10, x12, x14, x16
# CHECK: error:

pair.sub64 x10, x13, x14
# CHECK: error: {{.*}}even{{.*}}

pair.sub.2x32 x10, x13, x14
# CHECK: error: {{.*}}even{{.*}}

pair.mul.2x32 x10, x13, x14
# CHECK: error: {{.*}}even{{.*}}

pair.xor64 x11, x12, x14
# CHECK: error: {{.*}}even{{.*}}
pair.and64 x10, x13, x14
# CHECK: error: {{.*}}even{{.*}}
pair.slli64 x10, x13, 1
# CHECK: error: {{.*}}even{{.*}}
pair.srli64 x11, x12, 32
# CHECK: error: {{.*}}even{{.*}}
pair.srai64 x10, x12, -1
# CHECK: error:
pair.rori64 x10, x12, 64
# CHECK: error:
