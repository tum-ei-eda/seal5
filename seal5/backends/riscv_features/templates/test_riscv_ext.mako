; RUN: clang --target=riscv${xlen} --print-supported-extensions | FileCheck --check-prefix CHECK %s

% for expected in expected_rows:
; CHECK: ${expected}
% endfor
