; ModuleID = 'mod'
source_filename = "mod"
target datalayout = "e-m:e-p:32:32-i64:64-n32-S128"
target triple = "riscv32-unknown-linux-gnu"

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(argmem: readwrite)
define void @implcv_machhNs(ptr noalias nocapture %rd, ptr nocapture readonly %rs1, ptr nocapture readonly %rs2, i32 %Is3) local_unnamed_addr #0 {
  %1 = getelementptr i16, ptr %rs1, i32 1
  %.v = load i16, ptr %1, align 2
  %2 = getelementptr i16, ptr %rs2, i32 1
  %.v1 = load i16, ptr %2, align 2
  %3 = sext i16 %.v to i32
  %4 = sext i16 %.v1 to i32
  %5 = mul nsw i32 %4, %3
  %rd.v = load i32, ptr %rd, align 4
  %6 = add i32 %5, %rd.v
  %7 = and i32 %Is3, 31
  %8 = ashr i32 %6, %7
  store i32 %8, ptr %rd, align 4
  ret void
}

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(argmem: readwrite) }
