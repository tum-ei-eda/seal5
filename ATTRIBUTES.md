
# SEAL5 Attributes

This document describes the custom CoreDSL2 attributes introduced by Seal5, including their scope, origin, type, and usage examples.

## Classifications

Attributes describing instruction behavior and control flow.

| Attribute | Scope | Origin | Description | Type | Example |
|-----------|-------|--------|-------------|------|---------|
| `HAS_SIDE_EFFECTS` | Instruction | SEAL5 | True if side effects may occur during instruction execution. | `Bool` | |
| `MAY_LOAD` | Instruction | SEAL5 | True if the instruction may read from memory. | `Bool` | |
| `MAY_STORE` | Instruction | SEAL5 | True if the instruction may write to memory. | `Bool` | |
| `IS_TERMINATOR` | Instruction | SEAL5 | True if the instruction is a return or similar. | `Bool` | |
| `IS_BRANCH` | Instruction | SEAL5 | True if the instruction may branch or jump. | `Bool` | |
| `HAS_CALL` | Instruction | SEAL5 | True if the instruction calls at least one non-inlined or external function. | `Bool` | |
| `HAS_LOOP` | Instruction | SEAL5 | True if the instruction contains one or more loops. | `Bool` | |

## Operands

Attributes describing operand roles, types, and register usage.

| Attribute | Scope | Origin | Description | Type | Example |
|-----------|-------|--------|-------------|------|---------|
| `USES` | Instruction | SEAL5 | List of implicit registers read by the instruction. | `List[String]` | `[[USES=[ACC]]]` |
| `DEFS` | Instruction | SEAL5 | List of implicit registers written by the instruction. | `List[String]` | `[[DEFS=[ACC]]]` |
| `IN` | Operand | SEAL5 | True if and only if the operand is an input. | `Bool` | |
| `OUT` | Operand | SEAL5 | True if and only if the operand is an output. | `Bool` | |
| `INOUT` | Operand | SEAL5 | True if the operand is both an input and an output. | `Bool` | |
| `UNUSED` | Operand | SEAL5 | True if the operand is neither read nor written (for error handling). | `Bool` | |
| `IS_REG` | Operand | SEAL5 | True if the operand is used as an index into a register bank. | `Bool` | |
| `IS_IMM` | Operand | SEAL5 | True if the operand value is a compile-time immediate. | `Bool` | |
| `IS_IMM_LEAF` | Operand | SEAL5 | True if the operand is an immediate leaf. (TODO: explain) | `Bool` | |
| `IS_UNROLL_IMM` | Operand | SEAL5 | True if the immediate operand should be unrolled during pattern generation. | `Bool` | |
| `TYPE` | Operand | SEAL5 | CDSL type for the operand bitfield. | `String` | `[[TYPE=unsigned<5>]]` |
| `REG_CLASS` | Operand | SEAL5 | Differentiates between register banks addressed by the operand. | `String` | `[[REG_CLASS="GPR"]]` |
| `REG_TYPE` | Operand | SEAL5 | CDSL type for the register element addressed by the operand. | `String` | `[[REG_TYPE=unsigned<32>]]` |

## Mapping

Attributes used for LLVM instruction and type mapping.

| Attribute | Scope | Origin | Description | Type | Example |
|-----------|-------|--------|-------------|------|---------|
| `LLVM_INSTR` | Instruction | USER/SEAL5 | Identifies the unique name of the LLVM instruction to avoid conflicts with existing instructions. | `String` | `[[LLVM_INSTR=C_NAND]]` |
| `COMPRESSED` | Instruction | USER | Maps a compressed instruction to the name of its uncompressed counterpart. | `String` | `[[COMPRESSED=NAND]]` |
| `LLVM_TYPE` | Operand | SEAL5 | Matching LLVM type for the CDSL operand. | `String` | `[[LLVM_TYPE="s5"]]` |

## Encoding

Attributes describing instruction encodings and decoder metadata.

| Attribute | Scope | Origin | Description | Type | Example |
|-----------|-------|--------|-------------|------|---------|
| `OPCODE` | Instruction | SEAL5 | Literal integer value of the RISC-V major opcode. | `Int` | `[[OPCODE=0b01010]]` |
| `OPCODE_NAME` | Instruction | SEAL5 | String representation of the RISC-V opcode space name. | `String` | `[[OPCODE_NAME="custom-1"]]` |
| `FUNCT3` | Instruction | SEAL5 | Literal integer value of the RISC-V funct3 encoding bitfield. | `Int` | `[[FUNCT3=0b100]]` |
| `FUNCT7` | Instruction | SEAL5 | Literal integer value of the RISC-V funct7 encoding bitfield. | `Int` | `[[FUNCT7=0b1111111]]` |
| `ENC_FORMAT` | Instruction | SEAL5 | Internally used metadata for grouping similar encodings. | `String` | `[[ENC_FORMAT="r-type (binop)"]]` |
| `ENC_PATTERN` | Instruction | SEAL5 | Internally used metadata for grouping similar encodings. | `String` | `[[ENC_PATTERN="???????CCCCCBBBBB???AAAAA???????"]]` |
| `ENC_MASK` | Instruction | SEAL5 | Annotation of the mask value used in the ISS/RTL decoder. | `Int` | `[[ENC_MASK=0x00007f]]` |
| `ENC_MATCH` | Instruction | SEAL5 | Annotation of the match value used in the ISS/RTL decoder. | `Int` | `[[ENC_MATCH=0x000037]]` |

## Knobs / Flags

Attributes controlling SEAL5 processing and code generation behavior.

| Attribute | Scope | Origin | Description | Type | Example |
|-----------|-------|--------|-------------|------|---------|
| `KEEP` | Instruction set / instruction | USER | Selects the set or instruction, overriding its name-based YAML filters. | `Bool` | `[[keep]]` |
| `DROP` | Instruction set / instruction | USER | Excludes the set or instruction, overriding its name-based YAML filters. | `Bool` | `[[drop]]` |
| `SKIP_PATTERN_GEN` | Instruction | USER/SEAL5 | Avoids PatternGen for an instruction, including when otherwise supported. | `Bool` | `[[skip_pattern_gen]]` |
| `AUTO_UNROLL_LOOP` | Instruction | USER/SEAL5 | Unrolls loop bodies if feasible. | `Bool` | |
| `AUTO_UNROLL_IMM` | Instruction | USER/SEAL5 | Instantiates one LLVM instruction per immediate value instead of a single generic one for pattern generation. | `Bool` | |
| `AUTO_INTRIN` | Instruction | USER/SEAL5 | Automatically populates information about intrinsic functions and builtins if not provided by the user. | `Bool` | |
| `INLINE` | Function | USER/SEAL5 | Inlines and flattens function behavior into the caller. | `Bool` | |

If any set is marked `keep`, unmarked sets are excluded unless selected by a YAML
`filter.sets.keep` expression. The same rule applies independently to instructions
in the retained sets. A `drop` attribute always excludes its target. Specifying
both `keep` and `drop` on the same target is an error. Opcode and encoding-size
filters still apply to instructions marked `keep`; a kept instruction cannot
rescue a dropped set. With no `keep` attributes, existing YAML filtering is
unchanged.

## Extension metadata

Instruction-set attributes can supply extension settings, for example:

```coredsl
InstructionSet XCoreVMac extends RV32I [[keep]] [[ver=1.0]] [[experimental]] [[arch=xcvmac]] [[feature=XCVMac]] {
    // ...
}
```

`ver` (or `version`), `arch`, and `feature` accept a literal value. Version
values retain their spelling, so `1.20` remains distinct from `1.2`.
`experimental` is a flag or accepts `true`/`false`. Explicit YAML extension
settings override the corresponding attributes; unspecified settings use the
attributes or the usual defaults. Set attributes are local to the declaration
and are not inherited from extended sets.
