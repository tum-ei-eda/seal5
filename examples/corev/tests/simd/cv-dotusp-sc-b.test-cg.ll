; ModuleID = '<stdin>'
source_filename = "mod"
target datalayout = "e-m:e-p:32:32-i64:64-n32-S128"
target triple = "riscv32-unknown-linux-gnu"

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(argmem: readwrite)
define void @implSEAL5_CV_DOTUSP_SC_B(ptr noalias writeonly align 4 captures(none) initializes((0, 4)) %rd, i32 %rs1.seal5_value, i32 %rs2.seal5_value) local_unnamed_addr #0 {
  %rs1.sroa.3.0.extract.shift = lshr i32 %rs1.seal5_value, 16
  %rs1.sroa.4.0.extract.shift = lshr i32 %rs1.seal5_value, 24
  %rs2.sroa.0.0.extract.trunc = trunc i32 %rs2.seal5_value to i8
  %1 = trunc i32 %rs1.seal5_value to i16
  %2 = and i16 %1, 255
  %3 = sext i8 %rs2.sroa.0.0.extract.trunc to i16
  %4 = mul nsw i16 %2, %3
  %5 = trunc i32 %rs1.seal5_value to i16
  %6 = lshr i16 %5, 8
  %7 = mul nsw i16 %6, %3
  %8 = sext i16 %4 to i32
  %9 = sext i16 %7 to i32
  %10 = add nsw i32 %9, %8
  %11 = trunc nuw i32 %rs1.sroa.3.0.extract.shift to i16
  %12 = and i16 %11, 255
  %13 = mul nsw i16 %12, %3
  %14 = sext i16 %13 to i32
  %15 = add nsw i32 %10, %14
  %16 = trunc nuw nsw i32 %rs1.sroa.4.0.extract.shift to i16
  %17 = mul nsw i16 %16, %3
  %18 = sext i16 %17 to i32
  %19 = add nsw i32 %15, %18
  store i32 %19, ptr %rd, align 4
  ret void
}

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(argmem: readwrite) }

; RUN: llc -mtriple=riscv32 -stop-after=instruction-select -mattr=+m,+gpr32v,+xcorevsimd %s -global-isel=1 -global-isel-abort=1 -verify-machineinstrs -o - \
  ; RUN: | FileCheck -check-prefix=RV32-MIR %s
  ; RUN: llc -mtriple=riscv32 -mattr=+m,+gpr32v,+xcorevsimd %s -global-isel=1 -global-isel-abort=1 -verify-machineinstrs -o - \
  ; RUN: | FileCheck -check-prefix=RV32-ASM %s
; ModuleID = 'mod'
; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(argmem: readwrite)
  ; RV32-MIR-LABEL: name: implSEAL5_CV_DOTUSP_SC_B
  ; RV32-MIR: {{^ *[^;]*}} SEAL5_CV_DOTUSP_SC_B_{{[ ,]}}
  ; RV32-MIR-NEXT: SW
  ; RV32-MIR-NEXT: PseudoRET
  ; RV32-ASM-LABEL: implSEAL5_CV_DOTUSP_SC_B:
  ; RV32-ASM: seal5.cv.dotusp.sc.b
  ; RV32-ASM-NEXT: sw
  ; RV32-ASM-NEXT: ret
