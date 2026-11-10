# SPDX-License-Identifier: Apache-2.0
"""PatternGen measurements, kept separate from import and execution evidence."""

import re
import math
from pathlib import Path

import yaml


def parse_statistics(output):
    """Keep every LLVM statistics group, including importer counters."""
    stats = {}
    active = False
    for line in output.splitlines():
        if "Statistics Collected" in line:
            active = True
        if active:
            match = re.match(r"^\s*(\d+)\s+(\S+)\s+-\s+(.*?)\s*$", line)
            if match:
                count, group, description = match.groups()
                stats.setdefault(group, {})[description] = int(count)
    return stats


def count_gisel_entries(table):
    """Expand the direct emitter's literal permutation loops, not arbitrary C++."""
    loop = r"for \(int R_\d+ = 0; R_\d+ < (\d+); R_\d+\+\+\)\s*"
    block = re.compile(r"((?:" + loop + r")*)\{\s*RuleMatcher RM\{Locs\};")
    if len(re.findall(r"\bfor\s*\(", table)) != len(re.findall(loop, table)):
        return None
    if re.search(r"\b(?:if|while)\s*\(", table):
        return None
    matches = list(block.finditer(table))
    if len(matches) != len(re.findall(r"RuleMatcher RM\{Locs\};", table)) or not matches:
        return None
    return sum(math.prod(int(n) for n in re.findall(loop, match.group(1))) for match in matches)


def write_statistics(
    dest, output, elapsed, gisel_table=False, skip_patterns=False, returncode=None, skip_formats=False
):
    """Write even failed/empty invocations; unavailable evidence stays null."""
    dest = Path(dest)
    stats = parse_statistics(output)
    generated = stats.get("pattern-gen", {}).get("Generated patterns")
    if generated is None:
        generated = len(re.findall(r"^\s*Pattern for\s+", output, re.MULTILINE))
    mode = (
        "llvmir"
        if skip_patterns and skip_formats
        else ("formats" if skip_patterns else "gisel_table" if gisel_table else "tablegen")
    )
    stats["seal5"] = {
        "schema_version": 1,
        "mode": mode,
        "generation_time_s": elapsed,
        "returncode": returncode,
        "n_patterns": 0 if skip_patterns else generated,
        "n_gisel_table_entries": (
            count_gisel_entries(dest.with_suffix(".inc").read_text())
            if gisel_table and dest.with_suffix(".inc").is_file()
            else 0
        ),
        "n_patterns_imported": stats.get("pattern-gen", {}).get("Imported patterns"),
        "n_patterns_matched": stats.get("pattern-gen", {}).get("Matched patterns"),
        "n_gisel_table_entries_matched": stats.get("pattern-gen", {}).get("Matched GISel table entries"),
        "tablegen_bytes": sum(
            path.stat().st_size
            for path in (dest, dest.with_name(dest.stem + "InstrFormat" + dest.suffix))
            if path.is_file() and mode != "llvmir"
        ),
        "gisel_table_bytes": (
            dest.with_suffix(".inc").stat().st_size if gisel_table and dest.with_suffix(".inc").is_file() else 0
        ),
        "gisel_table_patch_bytes": 0,
    }
    Path(str(dest) + ".stats").write_text(yaml.safe_dump(stats, sort_keys=True), encoding="utf-8")
    return stats


def instruction_metrics(dest, mode, status):
    """Read one invocation without conflating rules with instructions."""
    path = Path(str(dest) + ".stats")
    data = yaml.safe_load(path.read_text()) if path.is_file() and status != "skipped" else {}
    measured = data.get("seal5", {})
    raw = data.get("pattern-gen", {})
    count = measured.get("n_patterns", raw.get("Generated patterns", 0))
    values = {
        "n_extracted_patterns": count,
        "n_gisel_table_entries": measured.get("n_gisel_table_entries") if mode == "gisel_table" else 0,
        "n_gisel_table_entries_matched": (
            measured.get("n_gisel_table_entries_matched") if mode == "gisel_table" and count else 0
        ),
        "n_instructions": 1,
        "n_processed_instructions": int(status != "skipped"),
        "n_skipped": int(status == "skipped"),
        "n_failed": int(status == "failed"),
        "n_success": int(status == "success"),
        "tablegen_bytes": measured.get("tablegen_bytes"),
        "gisel_table_bytes": measured.get("gisel_table_bytes"),
        "gisel_table_patch_bytes": measured.get("gisel_table_patch_bytes"),
        "pattern_gen_time_s": measured.get("generation_time_s"),
        "tablegen_time_s": measured.get("generation_time_s") if mode == "tablegen" else 0,
        "gisel_table_time_s": measured.get("generation_time_s") if mode == "gisel_table" else 0,
    }
    for kind in ("tablegen", "gisel_table"):
        values[f"n_{kind}_patterns"] = count if mode == kind else 0
        for evidence in ("imported", "matched"):
            if kind == "gisel_table" and evidence == "imported":
                continue
            values[f"n_{kind}_patterns_{evidence}"] = (
                measured.get(f"n_patterns_{evidence}") if mode == kind and count else 0
            )
    if status == "skipped":
        values = {key: 0 for key in values}
        values.update(n_instructions=1, n_skipped=1)
    return values


def aggregate(rows):
    """Never silently turn partial validation or timing into a complete total."""
    if not rows:
        result = {
            key: 0
            for key in (
                "n_extracted_patterns",
                "n_instructions",
                "n_processed_instructions",
                "n_skipped",
                "n_failed",
                "n_success",
                "tablegen_bytes",
                "gisel_table_bytes",
                "gisel_table_patch_bytes",
                "pattern_gen_time_s",
                "tablegen_time_s",
                "gisel_table_time_s",
                "n_tablegen_patterns",
                "n_gisel_table_patterns",
                "n_gisel_table_entries",
            )
        }
        for key in (
            "n_tablegen_patterns_imported",
            "n_tablegen_patterns_matched",
            "n_gisel_table_patterns_matched",
            "n_gisel_table_entries_matched",
        ):
            result.update({key: 0, key + "_known": 0, key + "_unreported_instructions": 0})
        return result
    result = {}
    for key in rows[0]:
        values = [row[key] for row in rows]
        result[key] = None if any(value is None for value in values) else sum(values)
        if key.endswith(("_imported", "_matched")):
            result[key + "_known"] = sum(value for value in values if value is not None)
            result[key + "_unreported_instructions"] = sum(value is None for value in values)
    return result


IDENTITY = {"model", "set", "instruction", "mode", "status"}


def report_rows(rows, scope="all"):
    """Aggregate unique set identities and preserve unavailable measurements."""
    output = []
    if scope in ("instruction", "all"):
        output.extend({"scope": "instruction", **row} for row in rows)
    groups = {}
    for row in rows:
        groups.setdefault((row["model"], row["set"]), []).append(row)
    if scope in ("set", "all"):
        for (model, name), members in sorted(groups.items()):
            output.append(
                {
                    "scope": "set",
                    "model": model,
                    "set": name,
                    **aggregate([{k: v for k, v in row.items() if k not in IDENTITY} for row in members]),
                    "n_sets": 1,
                    "n_processed_sets": int(any(row["n_processed_instructions"] for row in members)),
                }
            )
    if scope in ("global", "all"):
        output.append(
            {
                "scope": "global",
                **aggregate([{k: v for k, v in row.items() if k not in IDENTITY} for row in rows]),
                "n_sets": len(groups),
                "n_processed_sets": sum(
                    any(row["n_processed_instructions"] for row in members) for members in groups.values()
                ),
            }
        )
    return output
