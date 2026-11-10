; RUN: llc -mtriple=riscv${xlen} -mattr=${attrs_str} %s -o - | FileCheck --check-prefix CHECK-${label} %s

define void @test() {
; CHECK-${label}: .attribute 5, "${expected}"
  ret void
}
