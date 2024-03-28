; ModuleID = 'mod'
source_filename = "mod"
target datalayout = "e-m:e-p:32:32-i64:64-n32-S128"
target triple = "riscv32-unknown-linux-gnu"

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(argmem: readwrite)
define void @implcv_macs_i16(ptr noalias nocapture %rd, ptr nocapture readonly %rs1, ptr nocapture readonly %rs2) local_unnamed_addr #0 {
  %rs1.v = load i32, ptr %rs1, align 4
  %rs2.v = load i32, ptr %rs2, align 4
  %sext = shl i32 %rs1.v, 16
  %1 = ashr exact i32 %sext, 16
  %sext1 = shl i32 %rs2.v, 16
  %2 = ashr exact i32 %sext1, 16
  %3 = mul nsw i32 %2, %1
  %rd.v = load i32, ptr %rd, align 4
  %4 = add i32 %3, %rd.v
  store i32 %4, ptr %rd, align 4
  ret void
}

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(argmem: readwrite) }
