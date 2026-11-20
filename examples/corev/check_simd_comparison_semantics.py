# SPDX-License-Identifier: Apache-2.0
"""Check extracted packed comparison rules against independent lane semantics."""

import argparse
import operator
from pathlib import Path
import random
import re
import subprocess
from tempfile import TemporaryDirectory

WORD_MASK = 0xFFFFFFFF


def signed(value, bits=32):
    value &= (1 << bits) - 1
    return value - (1 << bits) if value >> (bits - 1) else value


def parse_pattern(text):
    tokens = iter(re.findall(r"\(|\)|[^\s(),]+", text))

    def parse(token):
        if token != "(":
            return token
        result = []
        for token in tokens:
            if token == ")":
                return result
            result.append(parse(token))
        raise ValueError("Unterminated pattern")

    result = parse(next(tokens))
    if next(tokens, None) is not None:
        raise ValueError("Trailing pattern tokens")
    return result


def evaluate(node, inputs, vector_type=None):
    if isinstance(node, str):
        return inputs[node.split(":$")[-1]] if ":$" in node else int(node)
    op, *args = node
    if re.fullmatch(r"v[24]i(?:8|16)", op):
        lanes, bits = map(int, re.fullmatch(r"v(\d+)i(\d+)", op).groups())
        value = evaluate(args[0], inputs, (lanes, bits))
        if isinstance(value, int):
            value = [(value >> (i * bits)) & ((1 << bits) - 1) for i in range(lanes)]
        return [lane & ((1 << bits) - 1) for lane in value]
    if op == "splat_vector":
        lanes, bits = vector_type
        return [evaluate(args[0], inputs) & ((1 << bits) - 1)] * lanes
    if op == "i32":
        return evaluate(args[0], inputs) & WORD_MASK
    if op == "setcc":
        left, right = (evaluate(arg, inputs) for arg in args[:2])
        pred = args[2]
        if not isinstance(left, list) and pred in ("SETLT", "SETLE", "SETGT", "SETGE"):
            left, right = signed(left), signed(right)
        relation = {
            "EQ": operator.eq,
            "NE": operator.ne,
            "LT": operator.lt,
            "LE": operator.le,
            "GT": operator.gt,
            "GE": operator.ge,
        }
        compare = relation[pred.removeprefix("SET").removeprefix("U")]
        if isinstance(left, list):
            bits = vector_type[1]
            if pred in ("SETLT", "SETLE", "SETGT", "SETGE"):
                left = [signed(lane, bits) for lane in left]
                right = [signed(lane, bits) for lane in right]
            return [-int(compare(a, b)) for a, b in zip(left, right)]
        return int(compare(left, right))
    left, right = (evaluate(arg, inputs) for arg in args)
    operations = {
        "or": operator.or_,
        "and": operator.and_,
        "xor": operator.xor,
        "add": operator.add,
        "mul": operator.mul,
        "sub": operator.sub,
        "shl": operator.lshift,
        "srl": operator.rshift,
        "sra": lambda a, b: signed(a) >> b,
    }
    return operations[op](left, right) & WORD_MASK


def reference(name, a, b):
    relation, mode, width = re.fullmatch(r"SEAL5_CV_CMP(EQ|NE|LTU?|LEU?|GTU?|GEU?)(?:_(SCI?))?_([BH])", name).groups()
    bits = 8 if width == "B" else 16
    mask = (1 << bits) - 1
    unsigned = relation.endswith("U") or relation in ("EQ", "NE")
    relation = relation.removesuffix("U")
    compare = {
        "EQ": operator.eq,
        "NE": operator.ne,
        "LT": operator.lt,
        "LE": operator.le,
        "GT": operator.gt,
        "GE": operator.ge,
    }[relation]
    result = 0
    for offset in range(0, 32, bits):
        left, right = (a >> offset) & mask, (b >> (0 if mode else offset)) & mask
        if not unsigned:
            left, right = signed(left, bits), signed(right, bits)
        if compare(left, right):
            result |= mask << offset
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="Directory containing PatternGen .td.out logs")
    parser.add_argument("--pattern-gen", type=Path, help="Also check scalar rules with packed comparisons disabled")
    args = parser.parse_args()
    boundaries = [
        0,
        1,
        0x7F,
        0x80,
        0xFF,
        0x7FFF,
        0x8000,
        0xFFFF,
        0x7F80FF00,
        0x807F00FF,
        0x7FFF8000,
        0x80007FFF,
        WORD_MASK,
    ]
    samples = [(a, b) for a in boundaries for b in boundaries]
    rng = random.Random(0)
    samples += [(rng.getrandbits(32), rng.getrandbits(32)) for _ in range(512)]
    instructions = set()
    checks = patterns = 0
    for path in sorted(args.directory.glob("SEAL5_CV_CMP*.td.out")):
        for name, text in re.findall(r"^Pattern for (\S+) \[[^\]]+\]: (.+)$", path.read_text(), re.M):
            tree = parse_pattern(text)
            instructions.add(name)
            patterns += 1
            immediate = "_SCI_" in name
            cases = samples
            if immediate:
                cases = [(a, signed(b, 6) if "seal5_simm6:$Imm6" in text else b) for a in boundaries for b in range(64)]
            for a, b in cases:
                actual = evaluate(tree, {"rs1": a, "rs2": b, "Imm6": b})
                if isinstance(actual, list):
                    bits = 32 // len(actual)
                    actual = sum(value << (i * bits) for i, value in enumerate(actual))
                expected = reference(name, a, b)
                if actual != expected:
                    raise AssertionError(f"{name}: a={a:#x}, b={b:#x}: {actual:#x} != {expected:#x}\n{text}")
                checks += 1
    assert len(instructions) == 60, f"Expected 60 instructions, found {len(instructions)}"
    print(f"Passed {checks} semantic checks across {patterns} rules for {len(instructions)} instructions")

    if args.pattern_gen is not None:
        sources = sorted(args.directory.glob("SEAL5_CV_CMP*_SC_*.core_desc"))
        assert len(sources) == 20, f"Expected 20 scalar-broadcast CoreDSL inputs, found {len(sources)}"
        scalar_checks = 0
        with TemporaryDirectory(prefix="seal5-scalar-compare-") as folder:
            for source in sources:
                result = subprocess.run(
                    [
                        str(args.pattern_gen),
                        str(source),
                        "-o",
                        str(Path(folder) / (source.stem + ".td")),
                        "--mattr",
                        "+gpr32v,+m,+xcorevsimd,-gpr32v-cmp",
                        "--riscv-xlen",
                        "32",
                        "--skip-formats",
                        "--skip-verify",
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                records = re.findall(r"^Pattern for (\S+) \[[^\]]+\]: (.+)$", result.stdout, re.M)
                assert len(records) == 1, f"Expected one scalar rule for {source.stem}"
                name, text = records[0]
                tree = parse_pattern(text)
                for a, b in samples[: len(boundaries) ** 2 + 128]:
                    actual = evaluate(tree, {"rs1": a, "rs2": b})
                    expected = reference(name, a, b)
                    if actual != expected:
                        raise AssertionError(f"{name}: scalar a={a:#x}, b={b:#x}: {actual} != {expected:#x}")
                    scalar_checks += 1
        print(f"Passed {scalar_checks} scalar comparison checks with packed comparison legalization disabled")


if __name__ == "__main__":
    main()
