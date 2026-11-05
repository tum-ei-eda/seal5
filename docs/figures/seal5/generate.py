#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Create publication figures from the registered Seal5 pass maps (stdlib only).

SVG generation needs Python 3. PDF/PNG export additionally needs Inkscape.
"""
import argparse
import ast
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import shutil
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
INK = "#172b3a"
MUTED = "#526370"
BLUE = "#23618c"
TEAL = "#187668"
AMBER = "#986019"
PALE = "#edf4f9"
GREEN = "#edf7f3"
WARM = "#fff6e7"
GLOBAL = {"seal5_td", "riscv_gisel_legalizer", "riscv_field_types", "riscv_gnu"}
OPTIONAL = {"explicit_memory_names", "explicit_register_names", "normalize_subscripts", "detect_branches", "riscv_gnu"}


def elem(parent, tag, **attrs):
    return ET.SubElement(parent, "{%s}%s" % (NS, tag), {k.replace("_", "-"): str(v) for k, v in attrs.items()})


class Figure:
    def __init__(self, width, height, title, description):
        self.root = ET.Element(
            "{%s}svg" % NS,
            {"width": f"{width/4}mm", "height": f"{height/4}mm", "viewBox": f"0 0 {width} {height}", "role": "img"},
        )
        elem(self.root, "title").text = title
        elem(self.root, "desc").text = description
        defs = elem(self.root, "defs")
        marker = elem(
            defs,
            "marker",
            id="arrow",
            markerWidth=8,
            markerHeight=8,
            refX=7,
            refY=4,
            orient="auto",
            markerUnits="userSpaceOnUse",
        )
        elem(marker, "path", d="M 0 0 L 8 4 L 0 8 z", fill=MUTED)
        elem(self.root, "rect", x=0, y=0, width=width, height=height, fill="white")

    def text(self, x, y, text, size=16, color=INK, bold=False, mono=False, anchor="start"):
        node = elem(
            self.root,
            "text",
            x=x,
            y=y,
            fill=color,
            font_size=size,
            font_family="DejaVu Sans Mono" if mono else "DejaVu Sans",
            font_weight="bold" if bold else "normal",
            text_anchor=anchor,
        )
        node.text = text
        return node

    def box(self, x, y, w, h, title, lines=(), fill=PALE, stroke=BLUE, optional=False, size=18):
        attrs = {"x": x, "y": y, "width": w, "height": h, "rx": 7, "fill": fill, "stroke": stroke, "stroke_width": 1.3}
        if optional:
            attrs["stroke_dasharray"] = "6 4"
        elem(self.root, "rect", **attrs)
        self.text(x + 16, y + 28, title, size=size, bold=True, color=stroke)
        for i, line in enumerate(lines):
            self.text(x + 16, y + 54 + i * 22, line, size=15)

    def arrow(self, points, dashed=False):
        elem(
            self.root,
            "polyline",
            points=" ".join(f"{x},{y}" for x, y in points),
            fill="none",
            stroke=MUTED,
            stroke_width=1.5,
            marker_end="url(#arrow)",
            stroke_dasharray="5 4" if dashed else "none",
        )

    def heading(self, title, subtitle):
        self.text(36, 43, title, size=27, bold=True)
        self.text(36, 72, subtitle, size=15, color=MUTED)

    def save(self, name):
        ET.indent(self.root)
        ET.ElementTree(self.root).write(OUT / f"{name}.svg", encoding="utf-8", xml_declaration=True)


def catalog():
    flow = ast.parse((ROOT / "seal5/flow.py").read_text())
    source = ast.parse((ROOT / "seal5/pass_list.py").read_text())
    functions = {n.name: n for n in source.body if isinstance(n, ast.FunctionDef)}
    maps = {}
    for node in flow.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id in ("TRANSFORM_PASS_MAP", "GENERATE_PASS_MAP"):
                maps[node.targets[0].id] = node.value.elts
    nested = next(
        n.value.elts
        for n in ast.walk(functions["pattern_gen_pass"])
        if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id == "pattern_gen_passes"
    )
    rows = []
    for key, nodes, prefix in [
        ("TRANSFORM_PASS_MAP", maps["TRANSFORM_PASS_MAP"], "T"),
        ("GENERATE_PASS_MAP", maps["GENERATE_PASS_MAP"], "G"),
        ("pattern_gen_passes", nested, "P"),
    ]:
        for i, node in enumerate(nodes, 1):
            name = ast.literal_eval(node.elts[0])
            handler = node.elts[1].attr if isinstance(node.elts[1], ast.Attribute) else node.elts[1].id
            fn = functions[handler]
            stages = sorted(
                {
                    n.attr
                    for n in ast.walk(fn)
                    if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "PatchStage"
                }
            )
            rows.append(
                {
                    "id": f"{prefix}{i:02}",
                    "name": name,
                    "handler": handler,
                    "scope": "GLOBAL" if prefix == "G" and name in GLOBAL else "MODEL",
                    "pipeline": key,
                    "patch_phases": ", ".join(stages),
                    "conditional": name in OPTIONAL,
                    "options": ast.unparse(node.elts[2]),
                    "source": "seal5/pass_list.py",
                    "line": fn.lineno,
                }
            )
    # Derive scopes from create_passes, rather than letting a figure silently drift.
    create = next(n for n in ast.walk(flow) if isinstance(n, ast.FunctionDef) and n.name == "create_passes")
    scope_lists = [set(ast.literal_eval(n)) for n in ast.walk(create) if isinstance(n, ast.List)]
    assert GLOBAL in scope_lists, "Pass-scope assignment changed; update the figure."
    assert [sum(r["id"].startswith(prefix) for r in rows) for prefix in ("T", "G", "P")] == [
        38,
        12,
        4,
    ], "Pass registration changed; update diagram layout and captions before regenerating."
    return rows


def stages():
    f = Figure(1400, 1000, "Seal5 stage sequence", "Sequential stages grouped by lifecycle role for a fresh run.")
    f.heading(
        "Seal5 stage sequence", "Fresh run with PatternGen; follow the numbered boxes left to right, then the next row."
    )
    groups = [
        (
            "Preparation",
            [
                ("reset", ["fresh-run reset"], True),
                ("initialize", ["LLVM checkout", "+ metadata"], False),
                ("load", ["CoreDSL, YAML", "and tests"], False),
                ("setup", ["dependencies", "+ support patches"], False),
                ("patch", ["phase 0", "bootstrap support"], False),
                ("build", ["bootstrap LLVM"], False),
            ],
        ),
        (
            "Construction",
            [
                ("transform", ["model passes"], False),
                ("generate", ["structural artifacts"], False),
                ("patch", ["phases 1–2"], False),
                ("build", ["instruction-aware LLVM", "PatternGen + llc"], False),
                ("generate", ["selection patterns"], False),
                ("patch", ["phases 3–5"], False),
                ("build", ["final LLVM"], False),
            ],
        ),
        ("Validation", [("test", ["imported + generated", "lit tests"], False)]),
        (
            "Delivery",
            [
                ("install", ["compiler installation"], True),
                ("deploy", ["LLVM source archive"], True),
                ("export", ["metadata + patches"], True),
                ("clean", ["final cleanup"], True),
            ],
        ),
    ]
    ordinal = 0
    for row, (title, items) in enumerate(groups):
        y = 108 + row * 200
        color = BLUE if row < 2 else TEAL
        fill = PALE if row < 2 else GREEN
        elem(f.root, "rect", x=28, y=y, width=1344, height=166, rx=10, fill="white", stroke=color, stroke_width=1)
        f.text(48, y + 29, title, 21, color, bold=True)
        width, gap = 164, 24
        start = (1400 - (len(items) * width + (len(items) - 1) * gap)) / 2
        for index, (name, lines, optional) in enumerate(items):
            ordinal += 1
            x = start + index * (width + gap)
            f.box(x, y + 46, width, 104, f"{ordinal:02}  {name}", fill=fill, stroke=color, optional=optional, size=17)
            for line_index, line in enumerate(lines):
                f.text(x + 12, y + 102 + line_index * 20, line, size=12)
            if index < len(items) - 1:
                f.arrow([(x + width, y + 98), (x + width + gap - 2, y + 98)])
        if row < len(groups) - 1:
            f.arrow([(700, y + 166), (700, y + 198)])
    f.text(
        36,
        937,
        "Dashed boxes: optional reset / delivery. Other operations can also be disabled through lifecycle flags.",
        14,
        MUTED,
    )
    f.text(
        36,
        960,
        (
            "The construction build groups the instruction-aware build and "
            "extraction-tool targets; see the full-flow figure for details."
        ),
        14,
        MUTED,
    )
    f.text(
        36,
        983,
        (
            "Source: seal5/wrapper.py · seal5/flow.py. LLVM "
            "patch-phase definitions are provided in the separate TeX table."
        ),
        13,
        MUTED,
    )
    f.save("01-stages")


def patch_phases():
    table = r"""% Generated by generate.py. Requires \usepackage{booktabs,tabularx}.
% Include in the dissertation with \input{01-patch-phases.tex}.
\begin{table}[tbp]
  \centering
  \small
  \caption{Seal5 LLVM patch phases and their default assignments.}
  \label{tab:seal5-patch-phases}
  \begin{tabularx}{\linewidth}{@{}l l >{\raggedright\arraybackslash}X@{}}
    \toprule
    \textbf{Phase} & \textbf{Purpose} & \textbf{Default contents} \\
    \midrule
    \texttt{PHASE\_0} & Bootstrap support &
      Insertion markers, PatternGen integration, and supporting backend changes. \\
    \addlinespace
    \texttt{PHASE\_1} & Structural integration &
      TableGen include scaffolding, ISA information, intrinsics, and GlobalISel legalizer integration. \\
    \addlinespace
    \texttt{PHASE\_2} & Instruction integration &
      Features, register definitions, operand field types, instruction definitions, and disassembler integration. \\
    \addlinespace
    \texttt{PHASE\_3} & Custom patches &
      No assignment from the currently registered generators; available to configured patches. \\
    \addlinespace
    \texttt{PHASE\_4} & Selection patterns &
      PatternGen-generated instruction-selection rules and associated artifacts. \\
    \addlinespace
    \texttt{PHASE\_5} & Custom patches &
      No assignment from the currently registered generators; available to configured patches. \\
    \bottomrule
  \end{tabularx}
  \par\smallskip
  {\footnotesize\raggedright
    Phases are applied in numeric order. These are default assignments;
    configuration can add or replace patches in any phase.\par}
\end{table}
"""
    (OUT / "01-patch-phases.tex").write_text(table)
    preview = r"""% Standalone preview; the dissertation should input 01-patch-phases.tex directly.
\documentclass{article}
\usepackage[paperwidth=190mm,paperheight=155mm,margin=10mm]{geometry}
\usepackage{booktabs,tabularx}
\pagestyle{empty}
\begin{document}
\input{01-patch-phases.tex}
\end{document}
"""
    (OUT / "01-patch-phases-preview.tex").write_text(preview)


def passes(rows):
    f = Figure(
        1530,
        1250,
        "Seal5 passes, order and scope",
        "All registered passes in execution order, with model/global scopes and nested PatternGen expansion.",
    )
    f.heading(
        "Seal5 passes: execution order and scope", "Read T01–T38, then G01–G11, then the expanded G12 pipeline P01–P04."
    )
    f.text(36, 101, "M = once per input model     G = once globally     * = conditional / opt-in", 15, MUTED)
    groups = [
        [r for r in rows if r["id"].startswith("T")][:19],
        [r for r in rows if r["id"].startswith("T")][19:],
        [r for r in rows if r["id"].startswith("G")],
    ]
    for col, group in enumerate(groups):
        x = 36 + col * 500
        f.text(x, 144, ["Transform · part 1", "Transform · part 2", "Generate"][col], 21, BLUE, bold=True)
        for i, row in enumerate(group):
            y = 166 + i * 45
            scope = "G" if row["scope"] == "GLOBAL" else "M"
            color = TEAL if scope == "G" else BLUE
            elem(
                f.root,
                "rect",
                x=x,
                y=y,
                width=458,
                height=35,
                rx=4,
                fill=GREEN if scope == "G" else PALE,
                stroke=color,
                stroke_width=0.7,
            )
            f.text(x + 9, y + 23, row["id"], 14, MUTED, mono=True)
            f.text(x + 56, y + 23, row["name"] + (" *" if row["conditional"] else ""), 14, mono=True)
            f.text(x + 438, y + 23, scope, 14, color, True, anchor="middle")
            if i < len(group) - 1:
                f.arrow([(x + 228, y + 35), (x + 228, y + 43)])
        if col < 2:
            f.text(x, 1051, "Continue at " + ("T20 →" if col == 0 else "G01 →"), 17, BLUE, bold=True)
    x = 1036
    f.text(x, 739, "G12 expands into:", 17, BLUE, bold=True)
    for i, row in enumerate(r for r in rows if r["id"].startswith("P")):
        y = 758 + i * 45
        elem(f.root, "rect", x=x + 20, y=y, width=438, height=35, rx=4, fill=PALE, stroke=BLUE, stroke_width=0.7)
        f.text(x + 29, y + 23, row["id"], 14, MUTED, mono=True)
        f.text(x + 78, y + 23, row["name"], 14, mono=True)
        f.text(x + 438, y + 23, "M", 14, BLUE, True, anchor="middle")
        if i < 3:
            f.arrow([(x + 238, y + 35), (x + 238, y + 43)])
    notes = [
        "Default wrapper: G01–G11 run before phases 1–2 are applied; G12 runs after PatternGen / llc are built.",
        (
            "Order follows the registered lists, not "
            "Seal5Pass.order. Passes are serial; model instances may run concurrently."
        ),
        (
            "All transforms and P01–P04 have MODEL scope. Four "
            "generators have GLOBAL scope. INSTR scope is not implemented;"
        ),
        (
            "SET is marked unsupported in the API and is not used by any "
            "registered pass. Splitting files per instruction does not change scope."
        ),
        (
            "* T33–T36 require enabled=true; G01 needs a GNU source "
            "tree. Filters and PatternGen eligibility can skip additional work."
        ),
        (
            "gen_model_td is an available handler but is not "
            "registered; it has no default execution position (MODEL, phase 1)."
        ),
        "Source: seal5/flow.py (pass maps + create_passes) · seal5/passes.py · seal5/pass_list.py (pattern_gen_pass)",
    ]
    for i, text in enumerate(notes):
        f.text(36, 1102 + i * 21, text, 14, MUTED)
    f.save("02-passes")


def full_flow():
    f = Figure(
        1360,
        1530,
        "Seal5 full compiler-generation flow",
        "Default fresh run including bootstrap builds, model processing, PatternGen, validation and delivery.",
    )
    f.heading("Seal5 full flow", "Fresh run with integrated PatternGen; optional controls are shown as annotations.")
    steps = [
        ("Initialize and load", ["Clone / select LLVM; create metadata", "Load CoreDSL, YAML configuration and tests"]),
        ("Setup and bootstrap patch", ["Fetch CoreDSL2LLVM dependency", "Apply PHASE_0 support patches"]),
        (
            "Initial LLVM build",
            ["Configure and compile the bootstrapped toolchain", "Skipped when reusing an existing build"],
        ),
        (
            "Transform models",
            ["T01–T38: convert, normalize, infer and annotate", "Create annotated Seal5 models + full CoreDSL"],
        ),
        (
            "Generate structural artifacts",
            ["G01–G11: instruction / target / frontend metadata", "Create patch indices and generated tests"],
        ),
        ("Patch and rebuild", ["Apply PHASE_1 and PHASE_2", "Build the instruction-aware LLVM toolchain"]),
        (
            "Build extraction tools",
            ["Build pattern-gen and llc", "Required before instruction-selection rule extraction"],
        ),
        (
            "Generate selection patterns",
            ["G12: P01–P04 (see detail at right)", "Produce TableGen patterns or direct GISel matchers"],
        ),
        (
            "Apply remaining phases",
            ["Apply PHASE_3 → PHASE_4 → PHASE_5", "PHASE_4 receives the generated selection rules"],
        ),
        ("Final LLVM build", ["Compile the retargeted compiler", "Includes the generated instruction-selection rules"]),
        (
            "Validate and deliver",
            ["Run imported + generated llvm-lit tests", "Optionally install, deploy sources, export metadata"],
        ),
    ]
    for i, (title, lines) in enumerate(steps):
        y = 112 + i * 116
        f.box(
            42,
            y,
            662,
            94,
            f"{i+1:02}  {title}",
            lines,
            fill=GREEN if i == 10 else PALE,
            stroke=TEAL if i == 10 else BLUE,
        )
        if i < len(steps) - 1:
            f.arrow([(373, y + 94), (373, y + 115)])
    f.box(
        780,
        112,
        538,
        144,
        "Inputs",
        [
            "CoreDSL architecture / instruction descriptions",
            "YAML: filters, extensions, passes and build settings",
            "C / LLVM IR / assembly test files",
        ],
        fill=GREEN,
        stroke=TEAL,
    )
    f.arrow([(780, 158), (704, 158)])
    f.box(
        780,
        292,
        538,
        144,
        "Model artifacts",
        [
            "CoreDSL → M2-ISA-R model → Seal5 model",
            "Instruction sets, operands, behavior and attributes",
            "Normalized behavior + per-model settings",
        ],
    )
    f.arrow([(704, 507), (744, 507), (744, 365), (780, 365)])
    f.box(
        780,
        486,
        538,
        136,
        "Generated integration",
        [
            "TableGen definitions; ISA / feature metadata",
            "Intrinsics / builtins; disassembler integration",
            "Patch indices + generated test sources",
        ],
    )
    f.arrow([(704, 622), (752, 622), (752, 550), (780, 550)])
    f.box(780, 680, 538, 407, "PatternGen detail · G12", fill=PALE, stroke=BLUE)
    f.text(800, 738, "P01  write_cdsl_compat", 16, mono=True)
    f.text(800, 762, "Reduced CoreDSL, split per instruction", 15, MUTED)
    f.text(800, 809, "P02  behav_to_llvmir", 16, mono=True)
    f.text(800, 833, "LLVM IR inspection artifact (.ll)", 15, MUTED)
    f.text(800, 880, "P03  llvmir_to_gmir", 16, mono=True)
    f.text(800, 904, "Generic MIR inspection artifact (.gmir)", 15, MUTED)
    f.text(800, 951, "P04  behav_to_pat", 16, mono=True)
    f.text(800, 975, "pattern-gen consumes reduced CoreDSL again", 15, MUTED)
    f.text(800, 1017, "Internally: behavior → LLVM IR → GMIR → matcher", 14, BLUE)
    f.text(800, 1042, "Output: .td patterns; optional direct .inc matchers", 14, BLUE)
    f.text(800, 1066, "P02 / P03 files are not direct inputs to P04.", 14, MUTED)
    f.arrow([(704, 970), (744, 970), (744, 715), (780, 715)])
    for y in (770, 841, 912):
        f.arrow([(1040, y), (1040, y + 15)], dashed=True)
    f.box(
        780,
        1128,
        538,
        143,
        "Outputs",
        [
            "Retargeted LLVM / Clang / assembler tools",
            "Test results, metrics and generated artifacts",
            "Optional installation and source / metadata archives",
        ],
        fill=GREEN,
        stroke=TEAL,
    )
    f.arrow([(704, 1320), (748, 1320), (748, 1200), (780, 1200)])
    notes = [
        "Execution controls: PREPATCHED reuses phase 0; RERUN suppresses the initial / intermediate all-target builds.",
        (
            "SKIP_PATTERNS omits extraction tools, G12 and phases 3–5. "
            "TEST_ONLY bypasses setup, generation, patching and builds."
        ),
        (
            "Lifecycle flags can disable individual operations; reset "
            "and final cleanup are optional. GNU patch generation is opt-in."
        ),
        (
            "Solid arrows: main execution / artifact relationships. "
            "Dashed arrows inside G12: pass order, not artifact dependencies."
        ),
        "Source: seal5/wrapper.py · seal5/flow.py · seal5/pass_list.py",
    ]
    for i, text in enumerate(notes):
        f.text(42, 1410 + i * 22, text, 14, MUTED)
    f.save("03-full-flow")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render", action="store_true", help="Export PDF and 160-dpi PNG using Inkscape")
    parser.add_argument(
        "--render-table", action="store_true", help="Compile the patch-phase table preview with pdflatex"
    )
    args = parser.parse_args()
    rows = catalog()
    stages()
    patch_phases()
    passes(rows)
    full_flow()
    with (OUT / "passes.csv").open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    manifest = {
        "source_files": {
            name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            for name in ["seal5/flow.py", "seal5/passes.py", "seal5/pass_list.py", "seal5/types.py", "seal5/wrapper.py"]
        },
        "counts": {"transforms": 38, "generators": 12, "nested_pattern_gen": 4},
        "scope_note": "Scopes extracted/checked against Seal5Flow.create_passes; not output file granularity.",
    }
    (OUT / "sources.json").write_text(json.dumps(manifest, indent=2) + "\n")
    if args.render:
        version = subprocess.check_output(["inkscape", "--version"], text=True)
        legacy = version.startswith("Inkscape 0.")
        for name in ("01-stages", "02-passes", "03-full-flow"):
            for ext in ("pdf", "png"):
                if legacy:
                    command = [
                        "inkscape",
                        "--without-gui",
                        str(OUT / f"{name}.svg"),
                        f'--export-{ext}={OUT/f"{name}.{ext}"}',
                        "--export-dpi=160",
                    ]
                else:
                    command = [
                        "inkscape",
                        str(OUT / f"{name}.svg"),
                        f"--export-type={ext}",
                        f'--export-filename={OUT/f"{name}.{ext}"}',
                        "--export-dpi=160",
                    ]
                subprocess.run(command, check=True)
    if args.render_table:
        with tempfile.TemporaryDirectory(prefix="seal5-table-") as temp:
            subprocess.run(
                [
                    "pdflatex",
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    f"-output-directory={temp}",
                    "01-patch-phases-preview.tex",
                ],
                cwd=OUT,
                check=True,
            )
            shutil.copyfile(Path(temp) / "01-patch-phases-preview.pdf", OUT / "01-patch-phases.pdf")
    print("Created three figures, the patch-phase TeX table, and pass/source catalogs in", OUT)


if __name__ == "__main__":
    main()
