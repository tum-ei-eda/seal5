; SPDX-License-Identifier: Apache-2.0
; Explicit vector IR distinguishes backend pair support from loop vectorization.
define <2 x i32> @add_vector(<2 x i32> %a, <2 x i32> %b) {
  %r = add <2 x i32> %a, %b
  ret <2 x i32> %r
}

define <2 x i32> @sub_vector(<2 x i32> %a, <2 x i32> %b) {
  %r = sub <2 x i32> %a, %b
  ret <2 x i32> %r
}

define <2 x i32> @mul_vector(<2 x i32> %a, <2 x i32> %b) {
  %r = mul <2 x i32> %a, %b
  ret <2 x i32> %r
}
