# SPDX-License-Identifier: Apache-2.0
"""Instruction, set and global reports for PatternGen experiments."""

import argparse
import json
import logging
from pathlib import Path

import pandas as pd
import yaml

from seal5.settings import Seal5Settings
from seal5.tools.pattern_metrics import instruction_metrics, report_rows


def collect_measurements(temp_dir):
    """Prefer current-run manifests; support older statistics as partial data."""
    rows = []
    covered = set()
    for manifest in sorted(Path(temp_dir).rglob("pattern_gen_manifest.json")):
        data = json.loads(manifest.read_text())
        if data["schema_version"] != 1:
            raise ValueError(f"Unsupported manifest version: {manifest}")
        rows.extend(data["instructions"])
        covered.add(manifest.parent)
    for path in sorted(Path(temp_dir).rglob("*.td.stats")):
        if any(parent in covered for parent in path.parents):
            continue
        dest = Path(str(path)[:-6])
        data = yaml.safe_load(path.read_text()) or {}
        mode = data.get("seal5", {}).get("mode", "tablegen")
        # Old artifacts cannot distinguish a failed extraction from a skipped one.
        status = "success" if dest.is_file() else "failed"
        rows.append(
            {
                "model": path.parent.parent.name,
                "set": path.parent.name,
                "instruction": dest.stem,
                "mode": mode,
                "status": status,
                **instruction_metrics(dest, mode, status),
            }
        )
    return rows


def apply_validation(rows, validation):
    """Attach explicit per-pattern evidence; never infer it from extraction."""
    by_key = {(row["model"], row["set"], row["instruction"], row["mode"]): row for row in rows}
    seen = set()
    for evidence in validation:
        key = tuple(evidence[name] for name in ("model", "set", "instruction", "mode"))
        if key not in by_key or key in seen:
            raise ValueError(f"Unknown or duplicate validation identity: {key}")
        seen.add(key)
        row = by_key[key]
        mode = row["mode"]
        if mode not in ("tablegen", "gisel_table"):
            raise ValueError(f"Cannot validate non-pattern invocation: {key}")
        count = row[f"n_{mode}_patterns"]
        for kind in ("imported", "matched", "matched_entries"):
            indices = evidence.get(kind)
            if indices is None:
                continue
            if not evidence.get(f"{kind}_source"):
                raise ValueError(f"Missing {kind} evidence source: {key}")
            if not isinstance(indices, list):
                raise ValueError(f"Expected pattern-index list: {key}")
            limit = row["n_gisel_table_entries"] if kind == "matched_entries" else count
            if kind == "matched_entries" and (mode != "gisel_table" or limit is None):
                raise ValueError(f"No known direct-entry population: {key}")
            if any(type(i) is not int or i < 0 or i >= limit for i in indices) or len(set(indices)) != len(indices):
                raise ValueError(f"Invalid {kind} pattern indices: {key}")
            if kind == "imported" and mode == "gisel_table":
                raise ValueError("Direct GISel entries bypass the SelectionDAG importer")
            field = "n_gisel_table_entries_matched" if kind == "matched_entries" else f"n_{mode}_patterns_{kind}"
            row[field] = len(indices)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", required=True)
    parser.add_argument("--fmt", choices=["auto", "csv", "pkl", "md", "json"], default="auto")
    parser.add_argument("--yaml", required=True)
    parser.add_argument("--scope", choices=["instruction", "set", "global", "all"], default="all")
    parser.add_argument("--agg", action="store_true", help="Alias for --scope global")
    parser.add_argument("--validation", help="JSON list of per-pattern import/match evidence")
    parser.add_argument("--print-df", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.log.upper()))
    settings = Seal5Settings.from_yaml_file(args.yaml)
    rows = collect_measurements(Path(settings.meta_dir) / "temp")
    if args.validation:
        rows = apply_validation(rows, json.loads(Path(args.validation).read_text()))
    result = report_rows(rows, "global" if args.agg else args.scope)
    df = pd.DataFrame(result)
    if args.print_df:
        print(df)
    out = Path(args.output)
    fmt = out.suffix[1:].lower() if args.fmt == "auto" else args.fmt
    if fmt == "csv":
        df.to_csv(out, index=False)
    elif fmt == "pkl":
        df.to_pickle(out)
    elif fmt == "md":
        df.to_markdown(out, index=False)
    elif fmt == "json":
        out.write_text(json.dumps(result, indent=2) + "\n")
    else:
        raise ValueError(f"Unsupported fmt: {fmt}")


if __name__ == "__main__":
    main()
