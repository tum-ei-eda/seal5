# SPDX-License-Identifier: Apache-2.0
"""Extension settings remain usable without a global RISC-V configuration."""
from types import SimpleNamespace
import sys

import pytest

from seal5.riscv_utils import get_riscv_defaults
from seal5.settings import RISCVSettings, Seal5Settings, ExtensionsSettings
from seal5.backends.riscv_intrinsics import writer


@pytest.mark.parametrize("width", [32, 64])
def test_configured_xlen_is_used_as_default(width):
    features, xlen = get_riscv_defaults(RISCVSettings(xlen=width, features=["zbb"]))
    assert xlen == width
    assert features == ["zbb"]


@pytest.mark.parametrize("level", ["model", "extension"])
def test_intrinsics_without_global_riscv_settings(level, tmp_path, monkeypatch):
    riscv = {"xlen": 64}
    settings = Seal5Settings.from_dict(
        {
            "models": {"Example": {"riscv": riscv if level == "model" else None}},
            "intrinsics": {
                "intrinsics": [
                    {
                        "set_name": "Custom",
                        "instr_name": "TEST",
                        "intrinsic_name": "test",
                        "ret_type": "i64",
                        "args": [{"arg_name": "rs1", "arg_type": "i64"}],
                    }
                ]
            },
        }
    )
    extension = ExtensionsSettings(arch="xcustom", riscv=RISCVSettings(xlen=64) if level == "extension" else None)
    settings.models["Example"].extensions = {"Custom": extension}
    model = SimpleNamespace(settings=settings, sets={"Custom": SimpleNamespace(settings=extension)})
    monkeypatch.setattr(writer, "load_model", lambda *a, **kw: model)
    monkeypatch.setattr(
        sys, "argv", ["writer", str(tmp_path / "Example.seal5model"), "-o", str(tmp_path / "intrin.patch")]
    )
    writer.main()
    assert "64bit" in (tmp_path / "intrin_target.patch").read_text()


@pytest.mark.parametrize("backend", ["llvmir", "patterngen"])
@pytest.mark.parametrize("global_features", [None, ["m"]])
def test_extraction_uses_each_extensions_settings(backend, global_features, tmp_path, monkeypatch):
    import importlib
    from pathlib import Path

    module = importlib.import_module(f"seal5.backends.{backend}.writer")
    settings = Seal5Settings.from_dict(
        {"models": {"Example": {}}, "riscv": {"features": global_features} if global_features else None}
    )
    sets = {}
    for name, width, feature in [("First", 64, "zbb"), ("Second", 32, "zba")]:
        extension = ExtensionsSettings(arch="x" + name.lower(), riscv=RISCVSettings(xlen=width, features=[feature]))
        instr = SimpleNamespace(name="TEST", attributes=[], mnemonic="test", operands={})
        sets[name] = SimpleNamespace(xlen=None, settings=extension, instructions={"TEST": instr})
        (tmp_path / name).mkdir()
        (tmp_path / name / "TEST.core_desc").touch()
    model = SimpleNamespace(settings=settings, sets=sets)
    monkeypatch.setattr(module, "load_model", lambda *a, **kw: model)
    calls = []

    def extract(*args, **kwargs):
        calls.append(kwargs)
        Path(args[2]).write_text("// generated fixture\n")
        return {}

    monkeypatch.setattr(module.cdsl2llvm, "run_pattern_gen", extract)
    monkeypatch.setenv("CDSL2LLVM_DIR", str(tmp_path))
    monkeypatch.setattr(
        sys, "argv", ["writer", str(tmp_path / "Example.seal5model"), "-o", str(tmp_path), "--splitted"]
    )
    module.main()
    assert [call["xlen"] for call in calls] == [64, 32]
    assert "+zbb" in calls[0]["mattr"] and "+zba" not in calls[0]["mattr"]
    assert "+zba" in calls[1]["mattr"] and "+zbb" not in calls[1]["mattr"]
