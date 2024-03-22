; ModuleID = 'mod'
source_filename = "mod"
target datalayout = "e-m:e-p:32:32-i64:64-n32-S128"
target triple = "riscv32-unknown-linux-gnu"

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(argmem: readwrite)
define void @implcv_macs_i32(ptr noalias nocapture %rd, ptr nocapture readonly %rs1, ptr nocapture readonly %rs2) local_unnamed_addr #0 {
  %rs1.v = load i32, ptr %rs1, align 4
  %rs2.v = load i32, ptr %rs2, align 4
  %1 = mul i32 %rs2.v, %rs1.v
  %rd.v = load i32, ptr %rd, align 4
  %2 = add i32 %1, %rd.v
  store i32 %2, ptr %rd, align 4
  ret void
}

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(argmem: readwrite) }
