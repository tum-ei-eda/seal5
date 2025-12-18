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

from mako.template import Template

from seal5.index import NamedPatch, TestFile, write_index_yaml
from seal5.settings import ExtensionsSettings, LLVMSettings
from seal5.model_utils import load_model

from .templates import template_dir


from seal5.logging import Logger

logger = Logger("backends.riscv_features")


def gen_riscv_features_str(
    name: str, ext_settings: ExtensionsSettings, llvm_settings: LLVMSettings, all_sets, generate_tests
):
    """Generate features string for LLVM patch."""
    # requires = ext_settings.requires
    implies = ext_settings.requires
    feature = ext_settings.get_feature(name=name)
    arch_ = ext_settings.get_arch(name=name)
    description = ext_settings.get_description(name=name)
    predicate = ext_settings.get_predicate(name=name)
    version = ext_settings.get_version()
    experimental = ext_settings.experimental
    vendor = ext_settings.vendor

    implied_features = set()
    implies_archs_with_ver = []
    if implies:
        for implied in implies:
            assert implied in all_sets
            implied_set_def = all_sets[implied]
            implied_ext_settings = implied_set_def.settings
            implied_feature = implied_ext_settings.get_predicate(name=implied)
            if generate_tests:
                implied_arch = implied_ext_settings.get_arch(name=implied)
                implied_version = implied_ext_settings.get_version()
                implied_version_str = str(implied_version).replace(".", "p")
                implied_arch_with_ver = implied_arch + implied_version_str
                implies_archs_with_ver.append(implied_arch_with_ver)
            # implied_features.add(f"Feature{implied_feature}")
            implied_features.add(f"Feature{implied_feature}")  # TODO: check missing Ext?

    legacy = True
    slim = False
    if llvm_settings:
        llvm_state = llvm_settings.state
        if llvm_state:
            llvm_version = llvm_state.version  # unused today, but needed very soon
            if llvm_version.major >= 19:
                legacy = False
                if llvm_version.major >= 20:
                    slim = True

    test_template_name = "test_riscv_attributes"
    if legacy:
        template_name = "riscv_features"
    else:
        if experimental:
            template_name = "riscv_features_experimental_new_slim" if slim else "riscv_features_experimental_new"
        else:
            template_name = "riscv_features_new_slim" if slim else "riscv_features_new"

    # TODO: make util!
    if not isinstance(version, str):
        assert isinstance(version, float)
        version = f"{version:.1f}"
    major, minor = list(map(int, version.split(".", 1)))

    content_template = Template(filename=str(template_dir / f"{template_name}.mako"))
    test_template = Template(filename=str(template_dir / f"{test_template_name}.mako"))
    if slim:
        # TODO: support experimental- prefix
        feature_lower = feature.lower()
        assert feature_lower == arch_, f"LLVM 20 requires matching arch and feature names ({feature_lower} vs. {arch_})"
        assert predicate == (f"Vendor{feature}" if vendor else f"StdExt{feature}")
    content_text = content_template.render(
        predicate=predicate,
        feature=feature,
        arch=arch_,
        description=description,
        major=major,
        minor=minor,
        implies="[" + ", ".join(implied_features) + "]",
    )
    test_files = {}
    if generate_tests:
        test_name = f"{arch_}.test-attrs.ll"
        xlen = ext_settings.riscv.xlen if ext_settings.riscv is not None else 32
        attrs_str = f"+{arch_}"
        label = arch_.upper()
        expected_archs = [f"{arch_}{major}p{minor}"]
        expected_archs += implies_archs_with_ver
        expected_archs_str = "_".join(expected_archs)
        expected = f"rv{xlen}i2p1_{expected_archs_str}"
        test_content = test_template.render(
            xlen=xlen,
            attrs_str=attrs_str,
            label=label,
            expected=expected,
        )
        test_files[test_name] = test_content
    return content_text + "\n", test_files


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
    parser.add_argument("--generate-tests", action="store_true")
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
    settings = model_obj.settings
    llvm_settings = None
    if settings.llvm:
        llvm_settings = settings.llvm
    artifacts = {}
    artifacts[None] = []  # used for global artifacts
    if not args.splitted:
        content = ""
        # errs = []
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
            content_, test_files_ = gen_riscv_features_str(
                set_name, ext_settings, llvm_settings, model_obj.sets, args.generate_tests
            )
            content += content_
            # test_files.update(test_files_)
            if args.generate_tests:
                for test_file, test_content in test_files_.items():
                    test_artifact = TestFile(
                        f"llvm/test/CodeGen/RISCV/seal5/generated/{test_file}", content=test_content
                    )
                    artifacts[set_name].append(test_artifact)
        content = content.rstrip()
        if len(content) > 0:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(content)
            riscv_features_patch = NamedPatch(
                "llvm/lib/Target/RISCV/RISCVFeatures.td", key="riscv_features", src_path=out_path
            )
            artifacts[None].append(riscv_features_patch)
    else:
        raise NotImplementedError
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
