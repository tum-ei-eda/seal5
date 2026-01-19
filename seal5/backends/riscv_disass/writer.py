# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Clean M2-ISA-R/Seal5 metamodel to .core_desc file."""

import argparse
import logging
import pathlib

import pandas as pd

# from mako.template import Template

from seal5.index import NamedPatch, write_index_yaml
from seal5.model_utils import load_model

# from .templates import template_dir


from seal5.logging import Logger

logger = Logger("backends.riscv_disass")


def main():
    """Main app entrypoint."""

    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", help="A .m2isarmodel or .seal5model file.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    # parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--splitted", action="store_true", help="Split per set")
    parser.add_argument("--formats", action="store_true", help="Also generate instruction formats")
    parser.add_argument("--metrics", default=None, help="Output metrics to file")
    parser.add_argument("--index", default=None, help="Output index to file")
    parser.add_argument("--ext", type=str, default="td", help="Default file extension (if using --splitted)")
    parser.add_argument("--compat", action="store_true")
    parser.add_argument("--generate-tests", action="store_true")
    args = parser.parse_args()

    # initialize logging
    logger.setLevel(getattr(logging, args.log.upper()))

    # resolve model paths
    top_level = pathlib.Path(args.top_level)
    # out_path = pathlib.Path(args.output)

    model_obj = load_model(top_level, compat=args.compat)

    metrics = {
        "n_sets": 0,
        "n_skipped": 0,
        "n_failed": 0,
        "n_success": 0,
        "skipped_sets": [],
        "failed_sets": [],
        "success_sets": [],
    }
    # preprocess model
    # print("model", model)
    settings = model_obj.settings
    llvm_settings = None
    if settings.llvm:
        llvm_settings = settings.llvm
    artifacts = {}
    artifacts[None] = []  # used for global artifacts

    from collections import defaultdict

    elen_extensions_map = defaultdict(list)
    if not args.splitted:
        # errs = []
        for set_name, set_def in model_obj.sets.items():
            print("set_name", set_name)
            ext_settings = set_def.settings
            print("ext_settings", ext_settings)
            if ext_settings is None:
                metrics["n_skipped"] += 1
                metrics["skipped_sets"].append(set_name)
                continue
            decoder_namespace = ext_settings.get_decoder_namespace(name=set_def.name)
            print("decoder_namespace", decoder_namespace)
            instr_sizes = set(instr_def.size for instr_def in set_def.instructions.values())
            print("instr_sizes", instr_sizes)
            artifacts[set_name] = []
            metrics["n_sets"] += 1
            metrics["n_success"] += 1
            metrics["success_sets"].append(set_name)
            for elen in instr_sizes:
                elen_extensions_map[elen].append((ext_settings, set_name))
            # content_, test_files_ = gen_riscv_features_str(
            #     set_name, ext_settings, llvm_settings, model_obj.sets, args.generate_tests
            # )
        # used_elens = list(elen_extensions_map.keys())
        # print("used_elens", used_elens)
        print("elen_extensions_map", elen_extensions_map)
        assert llvm_settings is not None
        llvm_state = llvm_settings.state
        assert llvm_state is not None
        llvm_version = llvm_state.version
        print("llvm_version", llvm_version)
        for elen, extensions in elen_extensions_map.items():
            print("elen", elen)
            print("extensions", extensions)
            if elen == 48:
                assert llvm_version.major >= 20
            if llvm_version.major >= 21:
                content = "TODO"
                riscv_disass_groups_patch = NamedPatch(
                    "llvm/lib/Target/RISCV/Disassembler/RISCVDisassembler.cpp",
                    key="riscv_disass_feature_groups",
                    content=content,
                )  # llvm21+
                artifacts[None].append(riscv_disass_groups_patch)
                # if is_group:
                #     else:
            else:
                assert llvm_version.major in [19, 20]
                lines = []
                for ext, set_name in extensions:
                    predicate = ext.get_predicate(name=set_name, with_has=False)
                    decoder_namespace = ext.get_decoder_namespace(name=set_name)
                    desc = ext.get_description(name=set_name)
                    line = (
                        f"TRY_TO_DECODE_FEATURE(RISCV::Feature{predicate}, DecoderTable{decoder_namespace}{elen},"
                        f'"{desc} opcode table");'
                    )
                    lines.append(line)
                content = "\n".join(lines)
                riscv_disass_decode_patch = NamedPatch(
                    "llvm/lib/Target/RISCV/Disassembler/RISCVDisassembler.cpp",
                    key=f"riscv_disass_decode_feature_{elen}",
                    content=content,
                    # src_path=out_path,
                )  # llvm20+
                artifacts[None].append(riscv_disass_decode_patch)
    else:
        raise NotImplementedError
    # input("!!!")
    if args.metrics:
        metrics_file = args.metrics
        metrics_file = args.metrics
        metrics_df = pd.DataFrame({key: [val] for key, val in metrics.items()})
        metrics_df.to_csv(metrics_file, index=False)
    if args.index:
        if sum(map(len, artifacts.values())) > 0:
            global_artifacts = artifacts.get(None, [])
            set_artifacts = {key: value for key, value in artifacts.items() if key is not None}
            index_file = args.index
            write_index_yaml(index_file, global_artifacts, set_artifacts, content=True)
        else:
            logger.warning("No patches generated. No index file will be written.")


if __name__ == "__main__":
    main()
