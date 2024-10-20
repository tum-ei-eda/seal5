# SPDX-License-Identifier: Apache-2.0
#
# This file is part of the M2-ISA-R project: https://github.com/tum-ei-eda/M2-ISA-R
#
# Copyright (C) 2022
# Chair of Electrical Design Automation
# Technical University of Munich

"""Generate Patches for RISCVRegisterInfo.td."""

import argparse
import logging
import pathlib
import pickle
from typing import Union

from m2isar.metamodel import arch

from seal5.index import NamedPatch, write_index_yaml

# from seal5.settings import ExtensionsSettings
from seal5.model import Seal5RegisterClass

logger = logging.getLogger("riscv_instr_info")


def write_riscv_register_info(reg):
    """Generate code for RISCVRegisterInfo.td LLVM patch."""
    # registers_template = Template(filename=str(template_dir / "registers_tablegen.mako"))

    # out_str = registers_template.render()
    out_str = f'def {reg.name} : RISCVReg<0, "{reg.name.lower()}">;'

    return out_str


def gen_riscv_register_info_str(set_def):
    """Generate full code for RISCVRegisterInfo.td patch for a set."""
    registers = set_def.registers
    register_groups = set_def.register_groups
    # print("registers", registers)
    # print("register_groups", register_groups)
    group_regs = {group_name: group.names for group_name, group in register_groups.items()}
    all_group_regs = [name for names in group_regs.values() for name in names]
    ret = []
    for group_name, group in register_groups.items():
        if group.reg_class == Seal5RegisterClass.GPR:
            continue  # Already supported
            # TODO: check size and width
        if group.reg_class == Seal5RegisterClass.FPR:
            raise NotImplementedError("Floating point registers not supported")
        if group.reg_class == Seal5RegisterClass.CSR:
            raise NotImplementedError("CSR registers not yet supported")
        if group.reg_class == Seal5RegisterClass.CUSTOM:
            raise NotImplementedError("Custom register goups not yet supported")
        raise ValueError(f"Unhandled case: {group.reg_class}")
    for reg_name, reg in registers.items():
        if reg_name in all_group_regs:
            logger.debug("Skipping group register %s", reg_name)
            continue
        assert reg.reg_class not in [Seal5RegisterClass.GPR, Seal5RegisterClass.FPR, Seal5RegisterClass.CSR]
        if reg.reg_class == Seal5RegisterClass.CUSTOM:
            assert reg.size == 1
            tablegen_str = write_riscv_register_info(reg)
            ret.append(tablegen_str)
        else:
            raise ValueError(f"Unhandled case: {reg.reg_class}")
            # width = reg.width
            # TODO: use width?
    # print("ret", ret)
    return "\n".join(ret)


def main():
    """Main app entrypoint."""

    # read command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("top_level", help="A .m2isarmodel or .seal5model file.")
    parser.add_argument("--log", default="info", choices=["critical", "error", "warning", "info", "debug"])
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--splitted", action="store_true", help="Split per set")
    parser.add_argument("--formats", action="store_true", help="Also generate instruction formats")
    parser.add_argument("--metrics", default=None, help="Output metrics to file")
    parser.add_argument("--index", default=None, help="Output index to file")
    parser.add_argument("--ext", type=str, default="td", help="Default file extension (if using --splitted)")
    args = parser.parse_args()

    # initialize logging
    logging.basicConfig(level=getattr(logging, args.log.upper()))

    # resolve model paths
    top_level = pathlib.Path(args.top_level)
    # abs_top_level = top_level.resolve()

    is_seal5_model = False
    # print("top_level", top_level)
    # print("suffix", top_level.suffix)
    if top_level.suffix == ".seal5model":
        is_seal5_model = True
    if args.output is not None:
        out_path = pathlib.Path(args.output)
    else:
        assert top_level.suffix in [".m2isarmodel", ".seal5model"], "Can not infer model type from file extension."
        raise NotImplementedError

        # out_path = top_level.parent / (top_level.stem + ".core_desc")

    logger.info("loading models")
    if not is_seal5_model:
        raise NotImplementedError

    # load models
    with open(top_level, "rb") as f:
        # models: "dict[str, arch.CoreDef]" = pickle.load(f)
        if is_seal5_model:
            model: "dict[str, Union[arch.InstructionSet, ...]]" = pickle.load(f)
            model["cores"] = {}
        else:  # TODO: core vs. set!
            temp: "dict[str, Union[arch.InstructionSet, arch.CoreDef]]" = pickle.load(f)
            assert len(temp) > 0, "Empty model!"
            if isinstance(list(temp.values())[0], arch.CoreDef):
                model = {"cores": temp, "sets": {}}
            elif isinstance(list(temp.values())[0], arch.InstructionSet):
                model = {"sets": temp, "cores": {}}
            else:
                assert False

    metrics = {
        "n_sets": 0,
        "n_skipped": 0,
        "n_failed": 0,
        "n_success": 0,
    }
    # preprocess model
    # print("model", model)
    # settings = model.get("settings", None)
    artifacts = {}
    artifacts[None] = []  # used for global artifacts
    if not args.splitted:
        content = ""
        for _, set_def in model["sets"].items():
            content_ = gen_riscv_register_info_str(set_def)
            if len(content_) > 0:
                content += content_
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
        register_info_patch = NamedPatch(
            "llvm/lib/Target/RISCV/RISCVRegisterInfo.td",
            key="riscv_register_info",
            src_path=out_path,
        )
        artifacts[None].append(register_info_patch)
    else:
        raise NotImplementedError("--splitted not supported")
    if args.metrics:
        # raise NotImplementedError("--metrics not implemented")
        metrics_file = args.metrics
        with open(metrics_file, "w", encoding="utf-8") as f:
            f.write(",".join(metrics.keys()))
            f.write("\n")
            f.write(",".join(map(str, metrics.values())))
            f.write("\n")
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
