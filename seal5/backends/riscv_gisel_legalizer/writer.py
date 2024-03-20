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

from seal5.index import NamedPatch, write_index_yaml
from seal5.settings import RISCVLegalizerSettings, Seal5Settings

logger = logging.getLogger("riscv_gisel_legalizer")

# if (ST.hasVendorXCvsimd()) {


def type_helper(ty):
    print("type_helper", ty)
    ty_ = ty.replace("seal5_", "")
    if ty_.startswith("p"):
        sz = ty_[1:]
        sz = int(sz)
        return f"const LLT {ty} = LLT::pointer({sz}, XLen);"
    elif ty_.startswith("s"):
        sz = ty_[1:]
        sz = int(sz)
        return f"const LLT {ty} = LLT::scalar({sz});"
    elif ty_.startswith("v"):
        n, sz = ty_[1:].split("i", 1)
        n = int(n)
        sz = int(sz)
        return f"const LLT {ty} = LLT::fixed_vector({n}, LLT::scalar({sz}));"
    else:
        raise RuntimeError(f"Unsupported: {ty}")


def gen_riscv_gisel_legalizer_str(legalizer_settings: RISCVLegalizerSettings):
    print("legalizer_settings", legalizer_settings)
    ops = legalizer_settings.ops
    used_types = []
    types_lines = []
    settings_lines = []
    if ops is None:
        return ""
    for op in ops:
        print("op", op)
        names = op.name
        print("names", names)
        types = op.types
        print("types", types)
        onlyif = op.onlyif
        print("onlyif", onlyif)
        if not isinstance(names, list):
            assert isinstance(names, str)
            names = [names]
        print("names'", names)
        if not isinstance(types, list):
            assert isinstance(types, str)
            names = [names]
        print("types'", types)
        types = [f"seal5_{ty}" for ty in types]
        types_str = "{" + ", ".join(types) + "}"
        for ty in types:
            if ty not in used_types:
                line = type_helper(ty)
                types_lines.append(line)
                used_types.append(ty)
        assert len(names) > 0
        if len(names) == 1:
            names_str = names[0]
        else:  # TODO: iterate over ops!
            raise NotImplementedError
            names_str = "{" + ", ".join(names) + "}"
        line = ""
        if onlyif:
            cond = " && ".join(["ST." + pred[0].lower() + pred[1:] + "()" for pred in onlyif])
            line += f"if ({cond}) "
        line += f"getActionDefinitionsBuilder({names_str}).legalFor({types_str});"
        settings_lines.append(line)

    print("used_types")
    ret = ""
    ret += "{\n"
    ret += "\n".join(types_lines)
    ret += "\n"
    ret += "\n".join(settings_lines)
    ret += "\n}"
    return ret


def main():
    """Main app entrypoint."""

    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", help="A .m2isarmodel or .seal5model file.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--metrics", default=None, help="Output metrics to file")
    parser.add_argument("--index", default=None, help="Output index to file")
    parser.add_argument("--ext", type=str, default="td", help="Default file extension (if using --splitted)")
    parser.add_argument("--yaml", type=str, default=None)
    args = parser.parse_args()

    # initialize logging
    logging.basicConfig(level=getattr(logging, args.log.upper()))

    # resolve model paths
    # top_level = pathlib.Path(args.top_level)
    # abs_top_level = top_level.resolve()

    # is_seal5_model = False
    # # print("top_level", top_level)
    # # print("suffix", top_level.suffix)
    # if top_level.suffix == ".seal5model":
    #     is_seal5_model = True
    # if args.output is None:
    #     assert top_level.suffix in [".m2isarmodel", ".seal5model"], "Can not infer model type from file extension."
    #     raise NotImplementedError

    #     # out_path = top_level.parent / (top_level.stem + ".core_desc")
    # else:
    assert args.output is not None
    out_path = pathlib.Path(args.output)

    assert args.yaml is not None
    assert pathlib.Path(args.yaml).is_file()
    settings = Seal5Settings.from_yaml_file(args.yaml)

    # logger.info("loading models")
    # if not is_seal5_model:
    #     raise NotImplementedError

    # load models

    artifacts = {}
    artifacts[None] = []  # used for global artifacts
    if settings:
        riscv_settings = settings.riscv
        if riscv_settings:
            legalization_settings = riscv_settings.legalization
            if legalization_settings:
                gisel_settings = legalization_settings.get("gisel", None)
                if gisel_settings:
                    content = gen_riscv_gisel_legalizer_str(gisel_settings)
                    if len(content) > 0:
                        with open(out_path, "w") as f:
                            f.write(content)
                        riscv_gisel_legalizer_patch = NamedPatch(
                            "llvm/lib/Target/RISCV/GISel/RISCVLegalizerInfo.cpp",
                            key="riscv_legalizer_info",
                            src_path=out_path,
                        )
                        artifacts[None].append(riscv_gisel_legalizer_patch)
    if args.metrics:
        raise NotImplementedError
        # metrics_file = args.metrics
        # with open(metrics_file, "w") as f:
        #     f.write(",".join(metrics.keys()))
        #     f.write("\n")
        #     f.write(",".join(map(str, metrics.values())))
        #     f.write("\n")
    if args.index:
        if sum(map(lambda x: len(x), artifacts.values())) > 0:
            global_artifacts = artifacts.get(None, [])
            set_artifacts = {key: value for key, value in artifacts.items() if key is not None}
            index_file = args.index
            write_index_yaml(index_file, global_artifacts, set_artifacts, content=True)
        else:
            logger.warning("No patches generated. No index file will be written.")


if __name__ == "__main__":
    main()
