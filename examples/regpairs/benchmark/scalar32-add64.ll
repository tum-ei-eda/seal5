; SPDX-License-Identifier: Apache-2.0
; Three-input scalar add handles the high word; carry remains explicit.
define internal i64 @seal5_scalar32_add64(i64 %a, i64 %b) alwaysinline nounwind memory(none) {
 %al = trunc i64 %a to i32
 %bl = trunc i64 %b to i32
 %as = lshr i64 %a, 32
 %bs = lshr i64 %b, 32
 %ah = trunc i64 %as to i32
 %bh = trunc i64 %bs to i32
 %lo = add i32 %al, %bl
 %overflow = icmp ult i32 %lo, %al
 %carry = zext i1 %overflow to i32
 %hi = call i32 asm ".insn r4 0x0b, 1, 0, $0, $1, $2, $3", "=r,r,r,r"(i32 %ah, i32 %bh, i32 %carry)
 %lowide = zext i32 %lo to i64
 %hiwide = zext i32 %hi to i64
 %shifted = shl i64 %hiwide, 32
 %result = or i64 %lowide, %shifted
 ret i64 %result
}
