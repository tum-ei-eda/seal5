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

from seal5.index import NamedPatch, write_index_yaml

# from seal5.settings import ExtensionsSettings
from seal5.model import Seal5RegisterClass
from seal5.model_utils import load_model

from seal5.logging import Logger

logger = Logger("backends.riscv_register_info")


def write_riscv_register_info(reg):
    """Generate code for RISCVRegisterInfo.td LLVM patch (RISCVReg)."""
    # registers_template = Template(filename=str(template_dir / "registers_tablegen.mako"))

    # out_str = registers_template.render()
    out_str = ""
    if reg.is_const:
        out_str += "let isConstant = true in\n  "
    out_str += f'def {reg.name} : RISCVReg<0, "{reg.name.lower()}">;'

    return out_str


def write_riscv_register_class_info(group_name, group, group_regs):
    """Generate code for RISCVRegisterInfo.td LLVM patch (RISCVRegisterClass)."""
    # registers_template = Template(filename=str(template_dir / "registers_tablegen.mako"))

    # out_str = registers_template.render()
    # TODO: get xlen?
    reg_width = group.reg_width
    # tablegen type infer fails for types < i32?
    reg_width = max(reg_width, 32)
    VT_LOOKUP = {
        Seal5RegisterClass.GPR: ("XLenVT", reg_width),
        Seal5RegisterClass.FPR: (f"f{reg_width}", reg_width),
        Seal5RegisterClass.CSR: ("XLenVT", reg_width),
        Seal5RegisterClass.CUSTOM: (f"i{reg_width}", reg_width),
    }
    vt_name, vt_size = VT_LOOKUP.get(group.reg_class)
    vt_names = [vt_name]
    vt_sizes = [vt_size]
    vts_str = ", ".join(vt_names)
    align = max(vt_sizes)
    lo = 0
    hi = group.size - 1
    alt = group.names[0] != f"{group_name}0"
    out_str = ""
    if group.reg_class == Seal5RegisterClass.CUSTOM:
        out_str += "let isAllocatable = 0 in\n  "
    # TODO: pass lo/hi to Seal5RegisterGroup
    if alt:
        seq_str = ", ".join(group.names)
    else:
        seq_str = f'(sequence "{group_name}%u", {lo}, {hi})'
    out_str += f"def {group_name} : RISCVRegisterClass<[{vts_str}], {align}, (add {seq_str})>;"

    return out_str


def gen_riscv_register_info_str(set_def):
    """Generate full code for RISCVRegisterInfo.td patch for a set."""
    registers = set_def.registers
    register_groups = set_def.register_groups
    # print("registers", registers)
    # print("register_groups", register_groups)
    group_regs = {group_name: group.names for group_name, group in register_groups.items()}
    # print("group_regs", group_regs)
    # all_group_regs = [name for names in group_regs.values() for name in names]
    # print("all_group_regs", all_group_regs)
    ret_groups = []
    to_skip = []
    for group_name, group in register_groups.items():
        if group.reg_class == Seal5RegisterClass.GPR:
            to_skip.extend(group.names)
            continue  # Already supported
            # TODO: check size and width
        if group.reg_class == Seal5RegisterClass.FPR:
            raise NotImplementedError("Floating point registers not supported")
        elif group.reg_class == Seal5RegisterClass.CSR:
            raise NotImplementedError("CSR registers not yet supported")
        elif group.reg_class == Seal5RegisterClass.CUSTOM:
            group_regs = [registers[name] for name in group.names]
            tablegen_str = write_riscv_register_class_info(group_name, group, group_regs)
            ret_groups.append(tablegen_str)
            # raise NotImplementedError("Custom register goups not yet supported")
        else:
            raise ValueError(f"Unhandled case: {group.reg_class}")
    ret = []
    for reg_name, reg in registers.items():
        if reg_name in to_skip:
            logger.debug("Skipping register %s", reg_name)
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
    return "\n".join(ret + ret_groups)


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
    parser.add_argument("--compat", action="store_true")
    args = parser.parse_args()

    # initialize logging
    logger.setLevel(getattr(logging, args.log.upper()))

    # resolve model paths
    top_level = pathlib.Path(args.top_level)
    out_path = pathlib.Path(args.output)

    model_obj = load_model(top_level, compat=args.compat)

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
        for _, set_def in model_obj.sets.items():
            content_ = gen_riscv_register_info_str(set_def)
            if len(content_) > 0:
                content += content_
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
        if len(content) > 0:
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
