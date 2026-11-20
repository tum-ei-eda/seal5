// Array thresholding with an invariant scalar threshold and a scalar tail.
// Explicit alignment is a caller contract; no unaligned-memory feature is used.
// RUN: clang --target=riscv32 -march=rv32im -O3 -Xclang -target-feature -Xclang +xcorevsimd -Rpass=loop-vectorize -S -emit-llvm %s -o %t.ll 2> %t.remarks
// RUN: FileCheck %s --check-prefix=VEC < %t.remarks
// RUN: FileCheck %s --check-prefix=IR < %t.ll
// RUN: llc -O3 -global-isel=0 -verify-machineinstrs %t.ll -o - | FileCheck %s --check-prefix=DAG
// RUN: llc -O3 -global-isel=1 -global-isel-abort=1 -verify-machineinstrs %t.ll -o - | FileCheck %s --check-prefix=GI
// VEC: vectorized loop (vectorization width: 4, interleaved count: 1)
// IR-LABEL: define{{.*}} @threshold_u8(
// IR: load <4 x i8>, ptr {{.*}}, align 4
// IR: icmp ult <4 x i8>
// IR: sext <4 x i1> {{.*}} to <4 x i8>
// IR: store <4 x i8> {{.*}}, ptr {{.*}}, align 4
// DAG-LABEL: threshold_u8:
// DAG: lw
// DAG: seal5.cv.{{(cmpltu(\.sc)?|cmpgtu)}}.b
// DAG: sw
// GI-LABEL: threshold_u8:
// GI: lw
// GI: seal5.cv.cmpltu.sc.b
// GI: sw
void threshold_u8(unsigned char *restrict out,
                  const unsigned char *restrict in,
                  unsigned char threshold, unsigned n) {
  out = __builtin_assume_aligned(out, 4);
  in = __builtin_assume_aligned(in, 4);
  for (unsigned i = 0; i < n; ++i)
    out[i] = -(in[i] < threshold);
}
