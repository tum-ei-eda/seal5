/* SPDX-License-Identifier: Apache-2.0 */
OUTPUT_ARCH(riscv)
ENTRY(_start)
SECTIONS {
  . = 0x80000000;
  .text : { *(.text.start) *(.text .text.*) }
  .rodata : { *(.rodata .rodata.*) }
  . = ALIGN(8);
  .data : { *(.data .data.*) }
  .sdata : { __global_pointer$ = . + 0x800; *(.sdata .sdata.*) }
  .tohost : { *(.tohost) }
  . = ALIGN(8);
  __bss_start = .;
  .bss : { *(.bss .bss.*) *(.sbss .sbss.*) *(COMMON) }
  . = ALIGN(8);
  __bss_end = .;
  _end = .;
  PROVIDE(end = .);
}
