; ModuleID = '<stdin>'
source_filename = "mod"
target datalayout = "e-m:e-p:32:32-i64:64-n32-S128"
target triple = "riscv32-unknown-linux-gnu"

; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(argmem: readwrite)
define void @implSEAL5_CV_SDOTUSP_SC_B(ptr noalias align 4 captures(none) %rd, i32 %rs1.seal5_value, i32 %rs2.seal5_value) local_unnamed_addr #0 {
  %rs1.sroa.3.0.extract.shift = lshr i32 %rs1.seal5_value, 16
  %rs1.sroa.4.0.extract.shift = lshr i32 %rs1.seal5_value, 24
  %rs2.sroa.0.0.extract.trunc = trunc i32 %rs2.seal5_value to i8
  %1 = trunc i32 %rs1.seal5_value to i16
  %2 = and i16 %1, 255
  %3 = sext i8 %rs2.sroa.0.0.extract.trunc to i16
  %4 = mul nsw i16 %2, %3
  %rd.v = load i32, ptr %rd, align 4
  %5 = sext i16 %4 to i32
  %6 = add i32 %rd.v, %5
  %7 = trunc i32 %rs1.seal5_value to i16
  %8 = lshr i16 %7, 8
  %9 = mul nsw i16 %8, %3
  %10 = sext i16 %9 to i32
  %11 = add i32 %6, %10
  %12 = trunc nuw i32 %rs1.sroa.3.0.extract.shift to i16
  %13 = and i16 %12, 255
  %14 = mul nsw i16 %13, %3
  %15 = sext i16 %14 to i32
  %16 = add i32 %11, %15
  %17 = trunc nuw nsw i32 %rs1.sroa.4.0.extract.shift to i16
  %18 = mul nsw i16 %17, %3
  %19 = sext i16 %18 to i32
  %20 = add i32 %16, %19
  store i32 %20, ptr %rd, align 4
  ret void
}

attributes #0 = { mustprogress nofree norecurse nosync nounwind willreturn memory(argmem: readwrite) }

; RUN: llc -mtriple=riscv32 -stop-after=instruction-select -mattr=+m,+gpr32v,+xcorevsimd %s -global-isel=1 -global-isel-abort=1 -verify-machineinstrs -o - \
  ; RUN: | FileCheck -check-prefix=RV32-MIR %s
  ; RUN: llc -mtriple=riscv32 -mattr=+m,+gpr32v,+xcorevsimd %s -global-isel=1 -global-isel-abort=1 -verify-machineinstrs -o - \
  ; RUN: | FileCheck -check-prefix=RV32-ASM %s
; ModuleID = 'mod'
; Function Attrs: mustprogress nofree norecurse nosync nounwind willreturn memory(argmem: readwrite)
  ; RV32-MIR-LABEL: name: implSEAL5_CV_SDOTUSP_SC_B
  ; RV32-MIR: {{^ *[^;]*}} SEAL5_CV_SDOTUSP_SC_B_{{[ ,]}}
  ; RV32-MIR-NEXT: SW
  ; RV32-MIR-NEXT: PseudoRET
  ; RV32-ASM-LABEL: implSEAL5_CV_SDOTUSP_SC_B:
  ; RV32-ASM: seal5.cv.sdotusp.sc.b
  ; RV32-ASM-NEXT: sw
  ; RV32-ASM-NEXT: ret
