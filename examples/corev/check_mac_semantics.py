# SPDX-License-Identifier: Apache-2.0
"""Check extracted MAC IR against 32-bit hardware arithmetic using constant folding."""

from pathlib import Path
import argparse
import re
import subprocess
from tempfile import TemporaryDirectory

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("directory", type=Path, help="PatternGen's XCoreVMac/XCoreVMac output directory")
parser.add_argument("--opt", default="opt", help="LLVM opt executable from the tested build")
args = parser.parse_args()
root = args.directory
pieces = []
checks = {}
samples = [
    (0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF),
    (0x80008000, 0x80008000, 0x7FFFFFFF),
    (0x7FFF7FFF, 0x7FFF7FFF, 0xFFFFFFFF),
    (0xFFFF0001, 0x8000FFFF, 0x80000000),
]
paths = [
    root / ("SEAL5_CV_" + name + ".ll")
    for name in [
        "MAC",
        "MSU",
        "MULUN",
        "MULHHUN",
        "MULSN",
        "MULHHSN",
        "MULURN",
        "MULHHURN",
        "MULSRN",
        "MULHHSRN",
        "MACUN",
        "MACHHUN",
        "MACSN",
        "MACHHSN",
        "MACURN",
        "MACHHURN",
        "MACSRN",
        "MACHHSRN",
    ]
]
for path in paths:
    if path.stem.endswith(".test-cg"):
        continue
    name = path.stem.removeprefix("SEAL5_CV_")
    text = path.read_text()
    bodies = re.findall(r"define void @impl.*?^}", text, re.M | re.S)
    if not bodies:
        raise ValueError(f"No extracted implementation functions in {path}")
    # Specialized modules add per-function alias metadata; the checks use distinct allocas.
    pieces.extend(re.sub(r", ![\w.]+ !\d+", "", re.sub(r" #\d+", "", body)) for body in bodies)
    shifts = [0] if name in ["MAC", "MSU"] else [0, 1, 5, 31]
    if f"@implSEAL5_CV_{name}_0(" in text:
        shifts = range(32)
    for k, (a, b, c) in enumerate(samples):
        for shift in shifts:
            hi = "HH" in name
            signed = "S" in name
            aa = (a >> (16 if hi else 0)) & 0xFFFF
            bb = (b >> (16 if hi else 0)) & 0xFFFF
            if signed:
                aa = aa - 65536 if aa & 32768 else aa
                bb = bb - 65536 if bb & 32768 else bb
            if name == "MAC":
                val = c + a * b
            elif name == "MSU":
                val = c - a * b
            else:
                val = aa * bb + (c if name.startswith("MAC") else 0) + ((1 << shift) >> 1 if name.endswith("RN") else 0)
                val &= 0xFFFFFFFF
                if signed and val & 0x80000000:
                    val -= 1 << 32
                val >>= shift
            expected = val & 0xFFFFFFFF
            expected = expected - (1 << 32) if expected & (1 << 31) else expected
            fn = f"check_{name}_{k}_{shift}"
            checks[fn] = expected
            callee = f"implSEAL5_CV_{name}"
            specialized = f"{callee}_{shift}"
            is_specialized = f"@{specialized}(" in text
            if is_specialized:
                callee = specialized
            call_args = "" if is_specialized or name in ["MAC", "MSU"] else f", i32 {shift}"
            pieces.append(
                f"""define i32 @{fn}() {{
 %rd=alloca i32
 %a=alloca i32
 %b=alloca i32
 store i32 {c}, ptr %rd
 store i32 {a}, ptr %a
 store i32 {b}, ptr %b
 call void @{callee}(ptr %rd, ptr %a, ptr %b{call_args})
 %v=load i32, ptr %rd
 ret i32 %v
}}"""
            )
text = "declare void @llvm.assume(i1)\n" + "\n".join(pieces)
with TemporaryDirectory() as directory:
    src = Path(directory) / "mac-semantics.ll"
    src.write_text(text)
    p = subprocess.run([args.opt, "-S", "-passes=default<O2>", str(src)], check=True, capture_output=True, text=True)
fail = []
for name, expected in checks.items():
    fn = re.search(r"define [^@]*@" + name + r"\(\).*?^}", p.stdout, re.M | re.S)[0]
    match = re.search(r"ret i32 (-?\d+)", fn)
    if not match or int(match[1]) != expected:
        fail.append((name, expected, fn))
print(f"{len(checks)} MAC semantic cases, {len(fail)} failures")
if fail:
    for failure in fail:
        print(failure)
    raise SystemExit(1)
