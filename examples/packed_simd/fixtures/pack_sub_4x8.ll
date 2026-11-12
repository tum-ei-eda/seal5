define i32 @packed_sub_4x8(i32 %a, i32 %b) {
  %av = bitcast i32 %a to <4 x i8>
  %bv = bitcast i32 %b to <4 x i8>
  %result = sub <4 x i8> %av, %bv
  %packed = bitcast <4 x i8> %result to i32
  ret i32 %packed
}
