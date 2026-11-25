"""Compatibility repair for local variable slice offsets in CoreDSL2LLVM."""

from seal5.tools.cdsl2llvm import fix_pattern_gen_slice_indices


def test_load_and_widen_offset_before_slice_arithmetic():
    source = """  Value upper = ParseExpression(ts, func, build);
  upper = build.CreateAdd(upper.ll, llvm::ConstantInt::get(upper.ll->getType(), len));
      fit_to_size(lower, build);
"""
    fixed = fix_pattern_gen_slice_indices(source)
    assert fixed.index("promote_lvalue(build, upper)") < fixed.index("build.CreateAdd")
    assert fixed.index("fit_to_size(upper, build)") < fixed.index("build.CreateAdd")
    assert "fit_to_size(*v, build)" in fixed
    assert fix_pattern_gen_slice_indices(fixed) == fixed


def test_unknown_parser_is_rejected():
    import pytest

    with pytest.raises(RuntimeError, match="Unrecognized PatternGen"):
        fix_pattern_gen_slice_indices("different parser")


def test_slice_semantics_with_pattern_gen(tmp_path):
    """Run with SEAL5_PATTERN_GEN_BIN pointing to a built LLVM bin directory."""
    import os
    import random
    import re
    import subprocess
    from pathlib import Path
    import pytest

    bindir = os.environ.get("SEAL5_PATTERN_GEN_BIN")
    if not bindir:
        pytest.skip("set SEAL5_PATTERN_GEN_BIN to run compiler integration tests")
    fixtures = Path(__file__).parent / "fixtures" / "pattern_gen"
    rng = random.Random(42)
    for fixture, instr, lanes, bits, stride, insert in (
        ("insert_half", "SEAL5_CV_INSERT_H", 2, 16, 16, True),
        ("extract_byte", "SEAL5_CV_EXTRACTU_B", 4, 8, 8, False),
        ("extract_unaligned", "SEAL5_CV_EXTRACTU_B", 25, 8, 1, False),
    ):
        output = tmp_path / f"{fixture}.ll"
        subprocess.run(
            [
                str(Path(bindir) / "pattern-gen"),
                str(fixtures / f"{fixture}.core_desc"),
                "--riscv-xlen=32",
                "--skip-patterns",
                "--skip-formats",
                "--mattr=+m,+gpr32v,+xcorevsimd",
                "-o",
                str(output),
            ],
            check=True,
            capture_output=True,
        )
        text = output.read_text()
        pieces, checks = [text], {}
        for lane in range(lanes):
            for i in range(32):
                a, b = rng.getrandbits(32), rng.getrandbits(32)
                mask = (1 << bits) - 1
                expected = (
                    ((a & ~(mask << (lane * stride))) | ((b & mask) << (lane * stride)))
                    if insert
                    else ((b >> (lane * stride)) & mask)
                )
                name = f"check_{lane}_{i}"
                checks[name] = expected
                pieces.append(
                    f"""define i32 @{name}() {{
 %rd = alloca i32, align 4
 %rs = alloca i32, align 4
 store i32 {a}, ptr %rd
 store i32 {b}, ptr %rs
 call void @impl{instr}(ptr %rd, ptr %rs, i32 {lane})
 %r = load i32, ptr %rd
 ret i32 %r
}}"""
                )
        output.write_text("\n".join(pieces))
        result = subprocess.run(
            [str(Path(bindir) / "opt"), "-S", "-passes=default<O2>", str(output)],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        for name, expected in checks.items():
            body = re.search(r"define [^@]*@" + name + r"\(\).*?^}", result, re.M | re.S)[0]
            value = re.search(r"ret i32 (-?\d+)", body)
            assert value and int(value[1]) & 0xFFFFFFFF == expected, body


def test_dynamic_slice_keeps_backing_storage_alignment():
    source = """struct Value {
  bool isLValue;
};
void promote_lvalue(llvm::IRBuilder<> &build, Value &v) {
  v.ll = build.CreateAlignedLoad(
      llvm::Type::getIntNTy(build.getContext(), v.bitWidth), v.ll,
      llvm::Align(ceil_to_pow2(v.bitWidth) / 8), v.ll->getName() + ".v");
  v.isLValue = false;
}
  Value upper = ParseExpression(ts, func, build);
  if (left.isLValue && alignedLower &&
  build.CreateAlignedStore(right.ll, left.ll,
"""
    fixed = fix_pattern_gen_slice_indices(source)
    assert "v.sliceOffset ? v.sliceStorageWidth : v.bitWidth" in fixed
    assert "llvm::Align(ceil_to_pow2(v.sliceOffset ? v.sliceStorageWidth : v.bitWidth) / 8)" in fixed
    assert "build.CreateAlignedLoad(storageTy, left.ll, llvm::Align(ceil_to_pow2(left.sliceStorageWidth) / 8))" in fixed
    assert "build.CreateAlignedStore(merged, left.ll, llvm::Align(ceil_to_pow2(left.sliceStorageWidth) / 8))" in fixed
    assert fix_pattern_gen_slice_indices(fixed) == fixed
    # Also repair a parser already processed by the previous adapter version.
    old = fixed.replace(
        "llvm::Align(ceil_to_pow2(v.sliceOffset ? v.sliceStorageWidth : v.bitWidth) / 8)",
        "llvm::Align(ceil_to_pow2(v.bitWidth) / 8)",
    ).replace("llvm::Align(ceil_to_pow2(left.sliceStorageWidth) / 8)", "llvm::Align(1)")
    assert fix_pattern_gen_slice_indices(old) == fixed


def test_dynamic_extract_pattern_has_no_synthetic_byte_loads(tmp_path):
    """Fresh pattern generation must keep a dynamic slice a register operation."""
    import os
    import subprocess
    from pathlib import Path
    import pytest

    bindir = os.environ.get("SEAL5_PATTERN_GEN_BIN")
    if not bindir:
        pytest.skip("set SEAL5_PATTERN_GEN_BIN to run compiler integration tests")
    source = Path(__file__).parent / "fixtures/pattern_gen/extract_unaligned.core_desc"
    output = tmp_path / "extract.td"
    subprocess.run(
        [
            str(Path(bindir) / "pattern-gen"),
            str(source),
            "-o",
            str(output),
            "--riscv-xlen=32",
            "--mattr=+m,+gpr32v",
            "--skip-formats",
            "--skip-verify",
            "--no-extend",
        ],
        check=True,
        capture_output=True,
    )
    pattern = output.read_text()
    assert "GPR:$rs1" in pattern and "srl" in pattern and "255" in pattern
    assert "load" not in pattern and "ptradd" not in pattern
    ir = output.with_suffix(".ll").read_text()
    assert "load i32, ptr %rs1, align 4" in ir
