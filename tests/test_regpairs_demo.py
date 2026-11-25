# SPDX-License-Identifier: Apache-2.0
"""The pair demo selects compatible inputs for both supported LLVM releases."""
from pathlib import Path
import runpy
import sys
import types

import pytest
import yaml


@pytest.mark.parametrize("version", [22, 23])
@pytest.mark.parametrize("style", ["explicit", "inferred"])
def test_pair_demo_release_inputs(monkeypatch, version, style):
    captured = {}
    wrapper = types.ModuleType("seal5.wrapper")
    wrapper.LLVM_REF = f"llvmorg-{version}.1.{8 if version == 22 else 3}"
    wrapper.run_seal5_flow = lambda files, **kwargs: captured.update(files=files)
    monkeypatch.setitem(sys.modules, "seal5.wrapper", wrapper)
    monkeypatch.setenv("PAIR_STYLE", style)
    runpy.run_path("examples/regpairs_demo.py")
    files = captured["files"]
    source = next(path for path in files if path.suffix == ".core_desc")
    assert source.is_file()
    assert ("inferred" in source.parts) == (style == "inferred")
    config = {}
    for path in files:
        if path.parent.name == "cfg" and path.name in ("regpairs.yml", "llvm22.yml"):
            config.update(yaml.safe_load(path.read_text()).get("tools", {}))
    assert config["pattern_gen"]["ref"].startswith(f"llvm-{version}.")
    pairs = yaml.safe_load(Path("examples/regpairs/cfg/regpairs.yml").read_text())["patches"]
    settings = types.SimpleNamespace(
        llvm=types.SimpleNamespace(state=types.SimpleNamespace(version=types.SimpleNamespace(major=version)))
    )
    selected = [p for p in pairs if "pair-" in p["file"] and eval(p["onlyif"], {"settings": settings})]
    assert len(selected) == 8
    for patch in selected:
        assert f"llvm{version}-pair-" in patch["file"]
        assert (Path("examples/regpairs/cfg") / patch["file"]).is_file()


def test_llvm22_pair_capability_patch_applies_before_definition_generation(tmp_path):
    """Stage 0 has empty markers, without any generated CORE-V definitions."""
    import subprocess

    relative = Path("llvm/lib/Target/RISCV/RISCVFeatures.td")
    source = tmp_path / relative
    source.parent.mkdir(parents=True)
    source.write_text(
        'def HasStdExtSvinval : Predicate<"Subtarget->hasStdExtSvinval()">,\n'
        "                       AssemblerPredicate<(all_of FeatureStdExtSvinval),\n"
        "                           \"'Svinval' (Fine-Grained Address-Translation Cache Invalidation)\">;\n"
        "\n"
        "// RISCVFeatures.td - riscv_features - INSERTION_START\n"
        "// RISCVFeatures.td - riscv_features - INSERTION_END\n"
        "\n"
        "def FeatureStdExtSvnapot\n"
        '    : RISCVExtension<1, 0, "NAPOT Translation Contiguity">;\n'
    )
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, capture_output=True)
    subprocess.run(["git", "add", str(relative)], cwd=tmp_path, check=True, capture_output=True)
    patch = Path("examples/regpairs/patches/llvm22-pair-capability.patch").resolve()
    subprocess.run(["git", "apply", "--index", str(patch)], cwd=tmp_path, check=True, capture_output=True)
    assert "def FeatureSeal5RegPair32 :" in source.read_text()
