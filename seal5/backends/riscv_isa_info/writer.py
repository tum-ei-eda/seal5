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
import re

import pandas as pd
from mako.template import Template

from seal5.index import NamedPatch, write_index_yaml
from seal5.settings import ExtensionsSettings, LLVMVersion
from seal5.model_utils import load_model

from seal5.logging import Logger

logger = Logger("backends.riscv_isa_info")


MAKO_TEMPLATE = '    {"${arch}", RISCVExtensionVersion{${version_major}, ${version_minor}}},'
MAKO_TEMPLATE_LLVM18 = '    {"${arch}", {${version_major}, ${version_minor}}},'


def gen_riscv_isa_info_str(name: str, ext_settings: ExtensionsSettings, llvm_version: LLVMVersion):
    # print("name", name)
    # print("ext_settings", ext_settings)
    arch_ = ext_settings.get_arch(name=name)
    version = ext_settings.get_version()
    if not isinstance(version, str):
        assert isinstance(version, (int, float))
        version = str(float(version))
    version_major, version_minor = str(version).split(".", 1)

    llvm_major = llvm_version.major
    template = MAKO_TEMPLATE_LLVM18 if llvm_major >= 18 else MAKO_TEMPLATE
    content_template = Template(template)
    content_text = content_template.render(arch=arch_, version_major=version_major, version_minor=version_minor)
    # content_text = content_text.rstrip("\n")
    return arch_, content_text


def gen_riscv_isa_info_metadata(model_sets, llvm_version: LLVMVersion):
    """Generate custom implication and incompatibility checks for RISCVISAInfo."""
    implications = set()
    incompatible = set()

    def get_arch(name):
        if name not in model_sets or model_sets[name].settings is None:
            raise ValueError(f"Unknown extension in RISCVISAInfo metadata: {name}")
        arch = model_sets[name].settings.get_arch(name=name)
        if re.fullmatch(r"[a-z][a-z0-9]*", arch) is None:
            raise ValueError(f"Invalid RISCVISAInfo extension name: {arch}")
        return arch

    for name, set_def in model_sets.items():
        ext_settings = set_def.settings
        if ext_settings is None:
            continue
        if not ext_settings.implies and not ext_settings.incompatible:
            continue
        arch = get_arch(name)
        for implied in ext_settings.implies or []:
            implications.add((arch, get_arch(implied)))
        for other in ext_settings.incompatible or []:
            other_arch = get_arch(other)
            if arch != other_arch:
                incompatible.add(tuple(sorted((arch, other_arch))))

    implies_text = ""
    for arch, implied in sorted(implications):
        if llvm_version.major < 18:
            add_extension = f'addExtension("{implied}", Version->Major, Version->Minor);'
        else:
            add_extension = f'addExtension("{implied}", Version.value());'
        implies_text += (
            f'    if (ExtName == "{arch}" && !WorkList.count("{implied}") && !Exts.count("{implied}")) {{\n'
            f'      auto Version = findDefaultVersion("{implied}");\n'
            f"      {add_extension}\n"
            f'      WorkList.insert("{implied}");\n'
            "    }\n"
        )

    incompatible_text = ""
    for first, second in sorted(incompatible):
        incompatible_text += (
            f'  if (Exts.count("{first}") && Exts.count("{second}"))\n'
            "    return createStringError(errc::invalid_argument,\n"
            f'                             "\'{first}\' and \'{second}\' extensions are incompatible");\n'
        )
    return implies_text, incompatible_text


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
        "skipped_sets": [],
        "failed_sets": [],
        "success_sets": [],
    }
    # preprocess model
    # print("model", model)
    artifacts = {}
    artifacts[None] = []  # used for global artifacts
    if not args.splitted:
        # content = ""
        contents = []  # Extensions need to be sorted!
        implications = ""
        incompatible = ""
        # errs = []
        settings = model_obj.settings
        llvm_version = None
        if settings:
            llvm_settings = settings.llvm
            if llvm_settings:
                llvm_state = llvm_settings.state
                if llvm_state:
                    llvm_version = llvm_state.version
        for set_name, set_def in model_obj.sets.items():
            artifacts[set_name] = []
            metrics["n_sets"] += 1
            ext_settings = set_def.settings
            if ext_settings is None:
                metrics["n_skipped"] += 1
                metrics["skipped_sets"].append(set_name)
                continue
            metrics["n_success"] += 1
            metrics["success_sets"].append(set_name)
            key, new_content = gen_riscv_isa_info_str(set_name, ext_settings=ext_settings, llvm_version=llvm_version)
            contents.append((key, new_content))
        implications, incompatible = gen_riscv_isa_info_metadata(model_obj.sets, llvm_version)
        contents = sorted(contents, key=lambda x: x[0])
        content = "\n".join([x[1] for x in contents])
        if len(content) > 0:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(content)
            if ext_settings.experimental:
                key = "riscv_isa_info_experimental"
            else:
                key = "riscv_isa_info"
            riscv_isa_info_patch = NamedPatch("llvm/lib/Support/RISCVISAInfo.cpp", key=key, src_path=out_path)
            artifacts[None].append(riscv_isa_info_patch)
        for key, metadata in (
            ("riscv_isa_info_implies", implications),
            ("riscv_isa_info_incompatible", incompatible),
        ):
            if metadata:
                metadata_path = out_path.with_name(f"{key}.patch")
                metadata_path.write_text(metadata, encoding="utf-8")
                artifacts[None].append(
                    NamedPatch("llvm/lib/Support/RISCVISAInfo.cpp", key=key, src_path=metadata_path)
                )
    else:
        raise NotImplementedError
    if args.metrics:
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
