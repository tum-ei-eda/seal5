define i32 @packed_add_2x16(i32 %a, i32 %b) {
  %av = bitcast i32 %a to <2 x i16>
  %bv = bitcast i32 %b to <2 x i16>
  %result = add <2 x i16> %av, %bv
  %packed = bitcast <2 x i16> %result to i32
  ret i32 %packed
}
