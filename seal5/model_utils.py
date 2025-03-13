"""Utilities for loading and dumping metamodels."""

import logging
from pathlib import Path
import pickle
from typing import Union

from m2isar.metamodel import M2_METAMODEL_VERSION, M2Model
from seal5.model import Seal5Model, SEAL5_METAMODEL_VERSION

logger = logging.getLogger("seal5_converter")


def load_model(
    model_path: Union[str, Path], compat: bool = False, allow_missmatch: bool = False
) -> Union[Seal5Model, M2Model]:
    logger.info("loading model: %s", str(model_path))
    with open(model_path, "rb") as f:
        # models: "dict[str, arch.CoreDef]" = pickle.load(f)
        # sets: "dict[str, arch.InstructionSet]" = pickle.load(f)
        model_obj: Union[Seal5Model, M2Model] = pickle.load(f)
    if compat:
        assert isinstance(model_obj, M2Model), "Expected M2Model"
    else:
        assert isinstance(model_obj, Seal5Model), "Expected Seal5Model"
    required_version = M2_METAMODEL_VERSION if compat else SEAL5_METAMODEL_VERSION
    if model_obj.model_version != required_version:
        err_handler = logger.warning if allow_missmatch else RuntimeError
        err_handler("Loaded model version mismatch")
    return model_obj


def dump_model(
    model_obj: Union[Seal5Model, M2Model], out_path: Union[str, Path], compat: bool = False, ignore_suffix: bool = False
):
    logger.info("dumping model")
    if not ignore_suffix:
        out_path = Path(out_path)
        suffix = out_path.suffix
        required_suffix = ".m2isarmodel" if compat else ".seal5model"
        if suffix not in [".m2isarmodel", ".seal5model"]:
            assert len(suffix) == 0, f"Invalid suffix: {suffix}"
            out_path = out_path.parent / f"{out_path.stem}{required_suffix}"
        else:
            assert suffix == required_suffix, f"Invalid suffix: {suffix}, Expected: {required_suffix}"
    with open(out_path, "wb") as f:
        pickle.dump(model_obj, f)
