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
    assert len(selected) == 5
    for patch in selected:
        assert f"llvm{version}-pair-" in patch["file"]
        assert (Path("examples/regpairs/cfg") / patch["file"]).is_file()
