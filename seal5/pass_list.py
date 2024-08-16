from pathlib import Path
from typing import Optional

from seal5 import utils
from seal5.tools import cdsl2llvm
from seal5.logging import get_logger
from seal5.index import File, NamedPatch, write_index_yaml
from seal5.passes import Seal5Pass, PassType, PassScope, PassManager, PassResult
from seal5.types import PatchStage
from seal5.settings import Seal5Settings, PatchSettings

logger = get_logger()


def sanitize_args(args):
    return [str(arg) if isinstance(arg, Path) else arg for arg in args]


def convert_models(
    input_model: str,
    settings: Optional[Seal5Settings] = None,
    env: Optional[dict] = None,
    verbose: bool = False,
    inplace: bool = False,
    use_subprocess: bool = False,
    prefix: Optional[str] = None,
    log_level: str = "debug",
    **kwargs,
):
    assert not inplace
    input_file = settings.models_dir / f"{input_model}.m2isarmodel"
    assert input_file.is_file(), f"File not found: {input_file}"
    name = input_file.name
    base = input_file.stem
    metrics = {"foo": "bar"}
    new_name = f"{base}.seal5model"
    logger.info("Converting %s -> %s", name, new_name)
    args = [
        settings.models_dir / name,
        "-o",
        settings.models_dir / new_name,
        "--log",
        log_level,
    ]
    if prefix:
        assert isinstance(prefix, str)
        args.extend(["--prefix", prefix])
    if not use_subprocess:
        from seal5.transform.converter import main as Converter

        args = sanitize_args(args)
        Converter(args)
    else:
        utils.python(
            "-m",
            "seal5.transform.converter",
            *args,
            env=env,
            print_func=logger.info if verbose else logger.debug,
            live=True,
        )
    return PassResult(metrics=metrics)


def optimize_model(
    input_model,
    settings: Optional[Seal5Settings] = None,
    env: Optional[dict] = None,
    verbose: bool = False,
    inplace: bool = True,
    use_subprocess: bool = False,
    log_level: str = "debug",
    **kwargs,
):
    assert inplace
    input_file = settings.models_dir / f"{input_model}.seal5model"
    assert input_file.is_file(), f"File not found: {input_file}"
    name = input_file.name
    logger.info("Optimizing %s", name)
    args = [
        settings.models_dir / name,
        "--log",
        log_level,
    ]
    if not use_subprocess:
        from seal5.transform.optimize_instructions import OptimizeInstructions

        args = sanitize_args(args)
        OptimizeInstructions(args)
    else:
        utils.python(
            "-m",
            "seal5.transform.optimize_instructions.optimizer",
            *args,
            env=env,
            print_func=logger.info if verbose else logger.debug,
            live=True,
        )


def infer_types(
    input_model: str,
    settings: Optional[Seal5Settings] = None,
    env: Optional[dict] = None,
    verbose: bool = False,
    inplace: bool = True,
    use_subprocess: bool = False,
    log_level: str = "debug",
    **kwargs,
):
    assert inplace
    input_file = settings.models_dir / f"{input_model}.seal5model"
    assert input_file.is_file(), f"File not found: {input_file}"
    name = input_file.name
    logger.info("Infering types for %s", name)
    args = [
        settings.models_dir / name,
        "--log",
        log_level,
    ]
    if not use_subprocess:
        from seal5.transform.infer_types import InferTypes

        args = sanitize_args(args)
        InferTypes(args)
    else:
        utils.python(
            "-m",
            "seal5.transform.infer_types.transform",
            *args,
            env=env,
            print_func=logger.info if verbose else logger.debug,
            live=True,
        )


def simplify_trivial_slices(
    input_model: str,
    settings: Optional[Seal5Settings] = None,
    env: Optional[dict] = None,
    verbose: bool = False,
    inplace: bool = True,
    use_subprocess: bool = False,
    log_level: str = "debug",
    **kwargs,
):
    assert inplace
    input_file = settings.models_dir / f"{input_model}.seal5model"
    assert input_file.is_file(), f"File not found: {input_file}"
    name = input_file.name
    logger.info("Simplifying trivial slices for %s", name)
    args = [
        settings.models_dir / name,
        "--log",
        log_level,
    ]
    if not use_subprocess:
        from seal5.transform.simplify_trivial_slices import SimplifyTrivialSlices

        args = sanitize_args(args)
        SimplifyTrivialSlices(args)
    else:
        utils.python(
            "-m",
            "seal5.transform.simplify_trivial_slices.transform",
            *args,
            env=env,
            print_func=logger.info if verbose else logger.debug,
            live=True,
        )


def explicit_truncations(
    input_model: str,
    settings: Optional[Seal5Settings] = None,
    env: Optional[dict] = None,
    verbose: bool = False,
    inplace: bool = True,
    use_subprocess: bool = False,
    log_level: str = "debug",
    **kwargs,
):
    assert inplace
    input_file = settings.models_dir / f"{input_model}.seal5model"
    assert input_file.is_file(), f"File not found: {input_file}"
    name = input_file.name
    logger.info("Adding excplicit truncations for %s", name)
    args = [
        settings.models_dir / name,
        "--log",
        log_level,
    ]
    if not use_subprocess:
        from seal5.transform.explicit_truncations import ExplicitTruncations

        args = sanitize_args(args)
        ExplicitTruncations(args)
    else:
        utils.python(
            "-m",
            "seal5.transform.explicit_truncations.transform",
            *args,
            env=env,
            print_func=logger.info if verbose else logger.debug,
            live=True,
        )


def process_settings(
    input_model: str,
    settings: Optional[Seal5Settings] = None,
    env: Optional[dict] = None,
    verbose: bool = False,
    inplace: bool = True,
    use_subprocess: bool = False,
    log_level: str = "debug",
    **kwargs,
):
    assert inplace
    input_file = settings.models_dir / f"{input_model}.seal5model"
    assert input_file.is_file(), f"File not found: {input_file}"
    name = input_file.name
    logger.info("Processing settings for %s", name)
    args = [
        settings.models_dir / name,
        "--log",
        log_level,
        "--yaml",
        settings.settings_file,
    ]
    if not use_subprocess:
        from seal5.transform.process_settings import ProcessSettings

        args = sanitize_args(args)
        ProcessSettings(args)
    else:
        utils.python(
            "-m",
            "seal5.transform.process_settings.transform",
            *args,
            env=env,
            print_func=logger.info if verbose else logger.debug,
            live=True,
        )


def filter_model(
    input_model: str,
    settings: Optional[Seal5Settings] = None,
    env: Optional[dict] = None,
    verbose: bool = False,
    inplace: bool = True,
    use_subprocess: bool = False,
    log_level: str = "debug",
    **kwargs,
):
    assert inplace
    input_file = settings.models_dir / f"{input_model}.seal5model"
    assert input_file.is_file(), f"File not found: {input_file}"
    name = input_file.name
    logger.info("Filtering %s", name)
    filter_settings = settings.filter
    filter_args = []

    def get_filter_args(settings, suffix):
        ret = []
        keep = list(map(str, settings.keep))
        drop = list(map(str, settings.drop))
        if keep:
            ret += [f"--keep-{suffix}", ",".join(keep)]
        if drop:
            ret += [f"--drop-{suffix}", ",".join(drop)]
        return ret

    filter_sets = filter_settings.sets
    filter_instructions = filter_settings.instructions
    filter_aliases = filter_settings.aliases
    filter_intrinsics = filter_settings.intrinsics
    filter_opcodes = filter_settings.opcodes
    filter_encoding_sizes = filter_settings.encoding_sizes
    # TODO: filter_functions
    filter_args.extend(get_filter_args(filter_sets, "sets"))
    filter_args.extend(get_filter_args(filter_instructions, "instructions"))
    filter_args.extend(get_filter_args(filter_aliases, "aliases"))
    filter_args.extend(get_filter_args(filter_intrinsics, "intrinsics"))
    filter_args.extend(get_filter_args(filter_opcodes, "opcodes"))
    filter_args.extend(get_filter_args(filter_encoding_sizes, "encoding-sizes"))
    args = [
        settings.models_dir / name,
        *filter_args,
        "--log",
        log_level,
    ]
    if not use_subprocess:
        from seal5.transform.filter_model import FilterModel

        args = sanitize_args(args)
        FilterModel(args)
    else:
        utils.python(
            "-m",
            "seal5.transform.filter_model.filter",
            *args,
            env=env,
            print_func=logger.info if verbose else logger.debug,
            live=True,
        )


def drop_unused(
    input_model: str,
    settings: Optional[Seal5Settings] = None,
    env: Optional[dict] = None,
    verbose: bool = False,
    inplace: bool = True,
    use_subprocess: bool = False,
    log_level: str = "debug",
    **kwargs,
):
    assert inplace
    input_file = settings.models_dir / f"{input_model}.seal5model"
    assert input_file.is_file(), f"File not found: {input_file}"
    name = input_file.name
    logger.info("Dropping unused for %s", name)
    args = [
        settings.models_dir / name,
        "--log",
        log_level,
    ]
    if not use_subprocess:
        from seal5.transform.drop_unused import DropUnused

        args = sanitize_args(args)
        DropUnused(args)
    else:
        utils.python(
            "-m",
            "seal5.transform.drop_unused.optimizer",
            *args,
            env=env,
            print_func=logger.info if verbose else logger.debug,
            live=True,
        )


def detect_registers(
    input_model: str,
    settings: Optional[Seal5Settings] = None,
    env: Optional[dict] = None,
    verbose: bool = False,
    inplace: bool = True,
    use_subprocess: bool = False,
    log_level: str = "debug",
    **kwargs,
):
    assert inplace
    input_file = settings.models_dir / f"{input_model}.seal5model"
    assert input_file.is_file(), f"File not found: {input_file}"
    name = input_file.name
    logger.info("Detecting registers for %s", name)
    args = [
        settings.models_dir / name,
        "--log",
        log_level,
    ]
    if not use_subprocess:
        from seal5.transform.detect_registers import main as DetectRegisters

        args = sanitize_args(args)
        DetectRegisters(args)
    else:
        utils.python(
            "-m",
            "seal5.transform.detect_registers",
            *args,
            env=env,
            print_func=logger.info if verbose else logger.debug,
            live=True,
        )


def detect_behavior_constraints(
    input_model: str,
    settings: Optional[Seal5Settings] = None,
    env: Optional[dict] = None,
    verbose: bool = False,
    inplace: bool = True,
    use_subprocess: bool = False,
    log_level: str = "debug",
    **kwargs,
):
    assert inplace
    input_file = settings.models_dir / f"{input_model}.seal5model"
    assert input_file.is_file(), f"File not found: {input_file}"
    name = input_file.name
    logger.info("Collecting constraints for %s", name)
    args = [
        settings.models_dir / name,
        "--log",
        log_level,
    ]
    if not use_subprocess:
        from seal5.transform.collect_raises import CollectRaises

        args = sanitize_args(args)
        CollectRaises(args)
    else:
        utils.python(
            "-m",
            "seal5.transform.collect_raises.collect",
            *args,
            env=env,
            print_func=logger.info if verbose else logger.debug,
            live=True,
        )


def detect_side_effects(
    input_model: str,
    settings: Optional[Seal5Settings] = None,
    env: Optional[dict] = None,
    verbose: bool = False,
    inplace: bool = True,
    use_subprocess: bool = False,
    log_level: str = "debug",
    **kwargs,
):
    assert inplace
    input_file = settings.models_dir / f"{input_model}.seal5model"
    assert input_file.is_file(), f"File not found: {input_file}"
    name = input_file.name
    logger.info("Detecting side effects for %s", name)
    args = [
        settings.models_dir / name,
        "--log",
        log_level,
    ]
    if not use_subprocess:
        from seal5.transform.detect_side_effects import DetectSideEffects

        args = sanitize_args(args)
        DetectSideEffects(args)
    else:
        utils.python(
            "-m",
            "seal5.transform.detect_side_effects.collect",
            *args,
            env=env,
            print_func=logger.info if verbose else logger.debug,
            live=True,
        )


def detect_inouts(
    input_model: str,
    settings: Optional[Seal5Settings] = None,
    env: Optional[dict] = None,
    verbose: bool = False,
    inplace: bool = True,
    use_subprocess: bool = False,
    log_level: str = "debug",
    **kargs,
):
    assert inplace
    input_file = settings.models_dir / f"{input_model}.seal5model"
    assert input_file.is_file(), f"File not found: {input_file}"
    name = input_file.name
    logger.info("Detecting inouts for %s", name)
    args = [
        settings.models_dir / name,
        "--log",
        log_level,
    ]
    if not use_subprocess:
        from seal5.transform.detect_inouts import DetectInouts

        args = sanitize_args(args)
        DetectInouts(args)
    else:
        utils.python(
            "-m",
            "seal5.transform.detect_inouts.collect",
            *args,
            env=env,
            print_func=logger.info if verbose else logger.debug,
            live=True,
        )


def collect_operand_types(
    input_model: str,
    settings: Optional[Seal5Settings] = None,
    env: Optional[dict] = None,
    verbose: bool = False,
    inplace: bool = True,
    use_subprocess: bool = False,
    log_level: str = "debug",
    **kwargs,
):
    assert inplace
    input_file = settings.models_dir / f"{input_model}.seal5model"
    assert input_file.is_file(), f"File not found: {input_file}"
    name = input_file.name
    logger.info("Collecting operand types for %s", name)
    args = [
        settings.models_dir / name,
        "--log",
        log_level,
        "--skip-failing",
    ]
    if not use_subprocess:
        from seal5.transform.collect_operand_types import CollectOperandTypes

        args = sanitize_args(args)
        CollectOperandTypes(args)
    else:
        utils.python(
            "-m",
            "seal5.transform.collect_operand_types.collect",
            *args,
            env=env,
            print_func=logger.info if verbose else logger.debug,
            live=True,
        )
    # input("<")


def collect_register_operands(
    input_model: str,
    settings: Optional[Seal5Settings] = None,
    env: Optional[dict] = None,
    verbose: bool = False,
    inplace: bool = True,
    use_subprocess: bool = False,
    log_level: str = "debug",
    **kwargs,
):
    assert inplace
    input_file = settings.models_dir / f"{input_model}.seal5model"
    assert input_file.is_file(), f"File not found: {input_file}"
    name = input_file.name
    logger.info("Collecting register operands for %s", name)
    args = [
        settings.models_dir / name,
        "--log",
        log_level,
    ]
    if not use_subprocess:
        from seal5.transform.collect_register_operands import CollectRegisterOperands

        args = sanitize_args(args)
        CollectRegisterOperands(args)
    else:
        utils.python(
            "-m",
            "seal5.transform.collect_register_operands.collect",
            *args,
            env=env,
            print_func=logger.info if verbose else logger.debug,
            live=True,
        )


def collect_immediate_operands(
    input_model: str,
    settings: Optional[Seal5Settings] = None,
    env: Optional[dict] = None,
    verbose: bool = False,
    inplace: bool = True,
    use_subprocess: bool = False,
    log_level: str = "debug",
    **kwargs,
):
    assert inplace
    input_file = settings.models_dir / f"{input_model}.seal5model"
    assert input_file.is_file(), f"File not found: {input_file}"
    name = input_file.name
    logger.info("Collecting immediate operands for %s", name)
    args = [
        settings.models_dir / name,
        "--log",
        log_level,
    ]
    if not use_subprocess:
        from seal5.transform.collect_immediate_operands import CollectImmediateOperands

        args = sanitize_args(args)
        CollectImmediateOperands(args)
    else:
        utils.python(
            "-m",
            "seal5.transform.collect_immediate_operands.collect",
            *args,
            env=env,
            print_func=logger.info if verbose else logger.debug,
            live=True,
        )


def eliminate_rd_cmp_zero(
    input_model: str,
    settings: Optional[Seal5Settings] = None,
    env: Optional[dict] = None,
    verbose: bool = False,
    inplace: bool = True,
    use_subprocess: bool = False,
    log_level: str = "debug",
    **kwargs,
):
    assert inplace
    input_file = settings.models_dir / f"{input_model}.seal5model"
    assert input_file.is_file(), f"File not found: {input_file}"
    name = input_file.name
    logger.info("Eliminating rd == 0 for %s", name)
    args = [
        settings.models_dir / name,
        "--log",
        log_level,
    ]
    if not use_subprocess:
        from seal5.transform.eliminate_rd_cmp_zero import EliminateRdCmpZero

        args = sanitize_args(args)
        EliminateRdCmpZero(args)
    else:
        utils.python(
            "-m",
            "seal5.transform.eliminate_rd_cmp_zero.transform",
            *args,
            env=env,
            print_func=logger.info if verbose else logger.debug,
            live=True,
        )


def eliminate_mod_rfs(
    input_model: str,
    settings: Optional[Seal5Settings] = None,
    env: Optional[dict] = None,
    verbose: bool = False,
    inplace: bool = True,
    use_subprocess: bool = False,
    log_level: str = "debug",
    **kwargs,
):
    assert inplace
    input_file = settings.models_dir / f"{input_model}.seal5model"
    assert input_file.is_file(), f"File not found: {input_file}"
    name = input_file.name
    logger.info("Eliminating op MOD RFS for %s", name)
    args = [
        settings.models_dir / name,
        "--log",
        log_level,
    ]
    if not use_subprocess:
        from seal5.transform.eliminate_mod_rfs import EliminateModRFS

        args = sanitize_args(args)
        EliminateModRFS(args)
    else:
        utils.python(
            "-m",
            "seal5.transform.eliminate_mod_rfs.transform",
            *args,
            env=env,
            print_func=logger.info if verbose else logger.debug,
            live=True,
        )


def write_yaml(
    input_model: str,
    settings: Optional[Seal5Settings] = None,
    env: Optional[dict] = None,
    verbose: bool = False,
    inplace: bool = True,
    use_subprocess: bool = False,
    log_level: str = "debug",
    **kwargs,
):
    assert inplace
    input_file = settings.models_dir / f"{input_model}.seal5model"
    assert input_file.is_file(), f"File not found: {input_file}"
    name = input_file.name
    new_name = name.replace(".seal5model", ".yml")
    logger.info("Writing YAML for %s", name)
    args = [
        settings.models_dir / name,
        "--log",
        log_level,
        "--output",
        settings.temp_dir / new_name,
    ]
    utils.python(
        "-m",
        "seal5.backends.yaml.writer",
        *args,
        env=env,
        print_func=logger.info if verbose else logger.debug,
        live=True,
    )
    new_settings: Seal5Settings = Seal5Settings.from_yaml_file(settings.temp_dir / new_name)
    settings.merge(new_settings, overwrite=False)


def write_cdsl(
    input_model: str,
    settings: Optional[Seal5Settings] = None,
    env: Optional[dict] = None,
    verbose: bool = False,
    inplace: bool = True,
    use_subprocess: bool = False,
    split: bool = False,
    compat: bool = False,
    log_level: str = "debug",
    **kargs,
):
    assert inplace
    input_file = settings.models_dir / f"{input_model}.seal5model"
    assert input_file.is_file(), f"File not found: {input_file}"
    name = input_file.name
    if split:
        new_name = name.replace(".seal5model", "")
    else:
        new_name = name.replace(".seal5model", ".core_desc")
    logger.info("Writing CDSL for %s", name)
    args = [
        settings.models_dir / name,
        "--log",
        log_level,
        "--output",
        settings.temp_dir / new_name,
    ]
    if split:
        (settings.temp_dir / new_name).mkdir(exist_ok=True)
        args.append("--splitted")
    if compat:
        args.append("--compat")
    utils.python(
        "-m",
        "seal5.backends.coredsl2.writer",
        *args,
        env=env,
        print_func=logger.info if verbose else logger.debug,
        live=True,
    )
    # args_compat = [
    #     settings.models_dir / name,
    #     "--log",
    #     # "info",
    #     "debug",
    #     "--output",
    #     settings.temp_dir / f"{new_name}_compat",
    #     "--compat",
    # ]
    # if split:
    #     args.append("--splitted")
    # utils.python(
    #     "-m",
    #     "seal5.backends.coredsl2.writer",
    #     *args_compat,
    #     env=env,
    #     print_func=logger.info if verbose else logger.debug,
    #     live=True,
    # )


# def write_cdsl_splitted(inplace: bool = True):
#     assert inplace
#     # input_files = list(settings.models_dir.glob("*.seal5model"))
#     # assert len(input_files) > 0, "No Seal5 models found!"
#     # for input_file in input_files:
#     #     name = input_file.name
#     #     sub = name.replace(".seal5model", "")
#     for _ in [None]:
#         set_names = list(settings.extensions.keys())
#         # print("set_names", set_names)
#         assert len(set_names) > 0, "No sets found"
#         for set_name in set_names:
#             insn_names = settings.extensions[set_name].instructions
#             if insn_names is None:
#                 logger.warning("Skipping empty set %s", set_name)
#                 continue
#             sub = settings.extensions[set_name].model
#             # TODO: populate model in yaml backend!
#             if sub is None:  # Fallback
#                 sub = set_name
#             input_file = settings.models_dir / f"{sub}.seal5model"
#             assert input_file.is_file(), f"File not found: {input_file}"
#             assert len(insn_names) > 0, f"No instructions found in set: {set_name}"
#             # insn_names = collect_instr_names()
#             (settings.temp_dir / sub / set_name).mkdir(exist_ok=True, parents=True)
#             for insn_name in insn_names:
#                 logger.info("Writing Metamodel for %s/%s/%s", sub, set_name, insn_name)
#                 args = [
#                     input_file,
#                     "--keep-instructions",
#                     insn_name,
#                     "--log",
#                     "debug",
#                     # "info",
#                     "--output",
#                     settings.temp_dir / sub / set_name / f"{insn_name}.seal5model",
#                 ]
#                 utils.python(
#                     "-m",
#                     "seal5.transform.filter_model.filter",
#                     *args,
#                     env=env,
#                     print_func=logger.info if verbose else logger.debug,
#                     live=True,
#                 )
#                 logger.info("Writing CDSL for %s/%s", sub, insn_name)
#                 args = [
#                     settings.temp_dir / sub / set_name / f"{insn_name}.seal5model",
#                     "--log",
#                     "debug",
#                     # "info",
#                     "--output",
#                     settings.temp_dir / sub / set_name / f"{insn_name}.core_desc"
#                 ]
#                 utils.python(
#                     "-m",
#                     "seal5.backends.coredsl2.writer",
#                     *args,
#                     env=env,
#                     print_func=logger.info if verbose else logger.debug,
#                     live=True,
#                 )
#                 args_compat = [
#                     settings.temp_dir / sub / set_name / f"{insn_name}.seal5model",
#                     "--log",
#                     # "info",
#                     "debug",
#                     "--output",
#                     settings.temp_dir / sub / set_name / f"{insn_name}.core_desc_compat",
#                     "--compat",
#                 ]
#                 utils.python(
#                     "-m",
#                     "seal5.backends.coredsl2.writer",
#                     *args_compat,
#                     env=env,
#                     print_func=logger.info if verbose else logger.debug,
#                     live=True,
#                 )


def convert_behav_to_llvmir(
    input_model: str,
    settings: Optional[Seal5Settings] = None,
    env: Optional[dict] = None,
    verbose: bool = False,
    split: bool = True,
    log_level: str = "debug",
    **kwargs,
):
    assert split, "TODO"
    gen_metrics_file = True
    input_file = settings.models_dir / f"{input_model}.seal5model"
    assert input_file.is_file(), f"File not found: {input_file}"
    name = input_file.name
    if split:
        new_name = name.replace(".seal5model", "")
    else:
        new_name = name.replace(".seal5model", ".ll")
    logger.info("Writing LLVM-IR for %s", name)
    args = [
        settings.models_dir / name,
        "--log",
        log_level,
        "--output",
        settings.temp_dir / new_name,
    ]
    if split:
        (settings.temp_dir / new_name).mkdir(exist_ok=True)
        args.append("--splitted")
    if gen_metrics_file:
        # TODO: move to .seal5/metrics
        metrics_file = settings.temp_dir / (new_name + "_llvmir_metrics.csv")
        args.extend(["--metrics", metrics_file])
    utils.python(
        "-m",
        "seal5.backends.llvmir.writer",
        *args,
        env=env,
        print_func=logger.info if verbose else logger.debug,
        live=True,
    )


def convert_behav_to_tablegen(
    input_model: str,
    settings: Optional[Seal5Settings] = None,
    env: Optional[dict] = None,
    verbose: bool = False,
    split: bool = True,
    formats: bool = True,
    patterns: bool = True,
    parallel: bool = False,
    log_level: str = "debug",
    **kwargs,
):
    assert split, "TODO"
    gen_metrics_file = True
    gen_index_file = True
    input_file = settings.models_dir / f"{input_model}.seal5model"
    assert input_file.is_file(), f"File not found: {input_file}"
    name = input_file.name
    if split:
        new_name = name.replace(".seal5model", "")
    else:
        new_name = name.replace(".seal5model", ".td")
    logger.info("Writing TableGen patterns for %s", name)
    # TODO: move to patches dir!
    args = [
        settings.models_dir / name,
        "--log",
        log_level,
        "--output",
        settings.temp_dir / new_name,
    ]
    if split:
        (settings.temp_dir / new_name).mkdir(exist_ok=True)
        args.append("--splitted")
    if formats:
        args.append("--formats")
    if patterns:
        args.append("--patterns")
    if gen_metrics_file:
        metrics_file = settings.temp_dir / (new_name + "_tblgen_patterns_metrics.csv")
        args.extend(["--metrics", metrics_file])
    if gen_index_file:
        index_file = settings.temp_dir / (new_name + "_tblgen_patterns_index.yml")
        args.extend(["--index", index_file])
    if parallel:
        import multiprocessing

        num_threads = multiprocessing.cpu_count()
        args.extend(["--parallel", str(num_threads)])
    utils.python(
        "-m",
        "seal5.backends.patterngen.writer",
        *args,
        env=env,
        print_func=logger.info if verbose else logger.debug,
        live=True,
    )
    if gen_index_file:
        if index_file.is_file():
            patch_name = f"tblgen_patterns_{input_file.stem}"
            patch_settings = PatchSettings(
                name=patch_name,
                stage=int(PatchStage.PHASE_4),
                comment=f"CDSL2LLVM Generated Tablegen Patterns for {input_file.name}",
                index=str(index_file),
                generated=True,
                target="llvm",
            )
            settings.add_patch(patch_settings)
            settings.to_yaml_file(settings.settings_file)
        else:
            logger.warning("No patches found!")


def gen_riscv_features_patch(
    input_model: str,
    settings: Optional[Seal5Settings] = None,
    env: Optional[dict] = None,
    verbose: bool = False,
    split: bool = False,
    log_level: str = "debug",
    **kwargs,
):
    assert not split, "TODO"
    # formats = True
    gen_metrics_file = True
    gen_index_file = True
    input_file = settings.models_dir / f"{input_model}.seal5model"
    assert input_file.is_file(), f"File not found: {input_file}"
    name = input_file.name
    new_name = name.replace(".seal5model", "")
    logger.info("Writing RISCVFeatures.td patch for %s", name)
    out_dir = settings.patches_dir / new_name
    out_dir.mkdir(exist_ok=True)

    args = [
        settings.models_dir / name,
        "--log",
        log_level,
        "--output",
        out_dir / "riscv_features.patch",
    ]
    if split:
        args.append("--splitted")
    if gen_metrics_file:
        metrics_file = out_dir / ("riscv_features_metrics.csv")
        args.extend(["--metrics", metrics_file])
    if gen_index_file:
        index_file = out_dir / ("riscv_features_index.yml")
        args.extend(["--index", index_file])
    utils.python(
        "-m",
        "seal5.backends.riscv_features.writer",
        *args,
        env=env,
        print_func=logger.info if verbose else logger.debug,
        live=True,
    )
    if gen_index_file:
        if index_file.is_file():
            patch_name = f"riscv_features_{input_file.stem}"
            patch_settings = PatchSettings(
                name=patch_name,
                stage=int(PatchStage.PHASE_2),
                comment=f"Generated RISCVFeatures.td patch for {input_file.name}",
                index=str(index_file),
                generated=True,
                target="llvm",
            )
            settings.add_patch(patch_settings)
            settings.to_yaml_file(settings.settings_file)
        else:
            logger.warning("No patches found!")


def gen_riscv_isa_info_patch(
    input_model: str,
    settings: Optional[Seal5Settings] = None,
    env: Optional[dict] = None,
    verbose: bool = False,
    split: bool = False,
    log_level: str = "debug",
    **kwargs,
):
    assert not split, "TODO"
    # formats = True
    gen_metrics_file = True
    gen_index_file = True
    input_file = settings.models_dir / f"{input_model}.seal5model"
    assert input_file.is_file(), f"File not found: {input_file}"
    name = input_file.name
    new_name = name.replace(".seal5model", "")
    logger.info("Writing RISCVISAInfo.cpp patch for %s", name)
    out_dir = settings.patches_dir / new_name
    out_dir.mkdir(exist_ok=True)

    args = [
        settings.models_dir / name,
        "--log",
        log_level,
        "--output",
        out_dir / "riscv_isa_info.patch",
    ]
    if split:
        args.append("--splitted")
    if gen_metrics_file:
        metrics_file = out_dir / ("riscv_isa_info_metrics.csv")
        args.extend(["--metrics", metrics_file])
    if gen_index_file:
        index_file = out_dir / ("riscv_isa_info_index.yml")
        args.extend(["--index", index_file])
    utils.python(
        "-m",
        "seal5.backends.riscv_isa_info.writer",
        *args,
        env=env,
        print_func=logger.info if verbose else logger.debug,
        live=True,
    )
    if gen_index_file:
        if index_file.is_file():
            patch_name = f"riscv_isa_info_{input_file.stem}"
            patch_settings = PatchSettings(
                name=patch_name,
                stage=int(PatchStage.PHASE_1),
                comment=f"Generated RISCVISAInfo.cpp patch for {input_file.name}",
                index=str(index_file),
                generated=True,
                target="llvm",
            )
            settings.add_patch(patch_settings)
            settings.to_yaml_file(settings.settings_file)
        else:
            logger.warning("No patches found!")


def gen_riscv_instr_info_patch(
    input_model: str,
    settings: Optional[Seal5Settings] = None,
    env: Optional[dict] = None,
    verbose: bool = False,
    split: bool = True,
    log_level: str = "debug",
    **kwargs,
):
    # assert not split, "TODO"
    assert split, "TODO"
    # formats = True
    gen_metrics_file = True
    gen_index_file = True
    input_file = settings.models_dir / f"{input_model}.seal5model"
    assert input_file.is_file(), f"File not found: {input_file}"
    name = input_file.name
    new_name = name.replace(".seal5model", "")
    logger.info("Writing RISCVInstrInfo.td patch for %s", name)
    out_dir = settings.patches_dir / new_name
    out_dir.mkdir(exist_ok=True)
    if split:
        out_path = out_dir / "riscv_instr_info"
        out_path.mkdir(exist_ok=True)
    else:
        out_path = out_dir / "riscv_instr_info.patch"

    args = [
        settings.models_dir / name,
        "--log",
        log_level,
        "--output",
        out_path,
    ]
    if split:
        args.append("--splitted")
    if gen_metrics_file:
        metrics_file = out_dir / ("riscv_instr_info_metrics.csv")
        args.extend(["--metrics", metrics_file])
    if gen_index_file:
        index_file = out_dir / ("riscv_instr_info_index.yml")
        args.extend(["--index", index_file])
    utils.python(
        "-m",
        "seal5.backends.riscv_instr_info.writer",
        *args,
        env=env,
        print_func=logger.info if verbose else logger.debug,
        live=True,
    )
    if gen_index_file:
        if index_file.is_file():
            patch_name = f"riscv_instr_info_{input_file.stem}"
            patch_settings = PatchSettings(
                name=patch_name,
                stage=int(PatchStage.PHASE_2),
                comment=f"Generated RISCVInstrInfo.td patch for {input_file.name}",
                index=str(index_file),
                generated=True,
                target="llvm",
            )
            settings.add_patch(patch_settings)
            settings.to_yaml_file(settings.settings_file)
        else:
            logger.warning("No patches found!")


def gen_riscv_gisel_legalizer_patch(
    input_model: str,
    settings: Optional[Seal5Settings] = None,
    env: Optional[dict] = None,
    verbose: bool = False,
    log_level: str = "debug",
    **kwargs,
):
    gen_metrics_file = False  # TODO
    gen_index_file = True
    assert input_model is None
    # input_file = settings.models_dir / f"{input_model}.seal5model"
    # assert input_file.is_file(), f"File not found: {input_file}"
    # name = input_file.name
    # new_name = name.replace(".seal5model", "")
    logger.info("Writing RISCVLegalizerInfo.cpp patch")
    out_dir = settings.patches_dir / "Seal5"
    out_dir.mkdir(exist_ok=True)

    args = [
        "none",
        "--yaml",
        settings.settings_file,
        "--log",
        log_level,
        "--output",
        out_dir / "riscv_gisel_legalizer.patch",
    ]
    if gen_metrics_file:
        metrics_file = out_dir / ("riscv_gisel_legalizer_metrics.csv")
        args.extend(["--metrics", metrics_file])
    if gen_index_file:
        index_file = out_dir / ("riscv_gisel_legalizer_index.yml")
        args.extend(["--index", index_file])
    utils.python(
        "-m",
        "seal5.backends.riscv_gisel_legalizer.writer",
        *args,
        env=env,
        print_func=logger.info if verbose else logger.debug,
        live=True,
    )
    if gen_index_file:
        if index_file.is_file():
            patch_name = "riscv_gisel_legalizer"
            patch_settings = PatchSettings(
                name=patch_name,
                stage=int(PatchStage.PHASE_1),
                comment="Generated RISCVLegalizerInfo.cpp patch",
                index=str(index_file),
                generated=True,
                target="llvm",
            )
            settings.add_patch(patch_settings)
            settings.to_yaml_file(settings.settings_file)
        else:
            logger.warning("No patches found!")
    # TODO: introduce global (model-independed) settings file


# def convert_behav_to_tablegen_splitted(inplace: bool = True):
#     assert inplace
#     # input_files = list(settings.models_dir.glob("*.seal5model"))
#     # assert len(input_files) > 0, "No Seal5 models found!"
#     errs = []
#     # for input_file in input_files:
#     #     name = input_file.name
#     #     sub = name.replace(".seal5model", "")
#     for _ in [None]:
#         set_names = list(settings.extensions.keys())
#         assert len(set_names) > 0, "No sets found"
#         for set_name in set_names:
#             insn_names = settings.extensions[set_name].instructions
#             if insn_names is None:
#                 logger.warning("Skipping empty set %s", set_name)
#                 continue
#             assert len(insn_names) > 0, f"No instructions found in set: {set_name}"
#             sub = settings.extensions[set_name].model
#             # TODO: populate model in yaml backend!
#             if sub is None:  # Fallbacke
#                 sub = set_name
#             for insn_name in insn_names:
#                 ll_file = settings.temp_dir / sub / set_name / f"{insn_name}.ll"
#                 if not ll_file.is_file():
#                     logger.warning("Skipping %s due to errors.", insn_name)
#                     continue
#                 # input_file = settings.temp_dir / sub / set_name / f"{insn_name}.core_desc_compat"
#                 input_file = settings.temp_dir / sub / set_name / f"{insn_name}.core_desc"
#                 assert input_file.is_file(), f"File not found: {input_file}"
#                 output_file = input_file.parent / (input_file.stem + ".td")
#                 name = input_file.name
#                 logger.info("Writing TableGen for %s", name)
#                 ext = settings.extensions[set_name].feature
#                 if ext is None:  # fallback to set_name
#                     ext = set_name.replace("_", "")
#                 try:
#                     cdsl2llvm.run_pattern_gen(settings.deps_dir / "cdsl2llvm" / "llvm" / "build",
# input_file, output_file,
# skip_patterns=False, skip_formats=False, ext=ext)
#                 except AssertionError:
#                     pass
#                     # errs.append((insn_name, str(ex)))
#     if len(errs) > 0:
#         # print("errs", errs)
#         for insn_name, err_str in errs:
#             print("Err:", insn_name, err_str)
#             input("!")


def convert_llvmir_to_gmir(
    input_model: str,
    settings: Optional[Seal5Settings] = None,
    env: Optional[dict] = None,
    verbose: bool = False,
    split: bool = True,
    inplace: bool = True,
    use_subprocess: bool = False,
    **kwargs,
):
    assert inplace
    assert split
    # input_files = list(settings.models_dir.glob("*.seal5model"))
    # assert len(input_files) > 0, "No Seal5 models found!"
    errs = []
    # for input_file in input_files:
    #     name = input_file.name
    #     sub = name.replace(".seal5model", "")
    default_mattr = "+m,+fast-unaligned-access"
    if settings:
        riscv_settings = settings.riscv
        if riscv_settings:
            xlen = riscv_settings.xlen
            features = riscv_settings.features
            if features is None:
                pass
            else:
                default_mattr = ",".join([f"+{f}" for f in features])
            if xlen == 64 and "+64bit" not in default_mattr:
                default_mattr = ",".join([*default_mattr.split(","), "+64bit"])
    for _ in [None]:
        set_names = list(settings.extensions.keys())
        assert len(set_names) > 0, "No sets found"
        for set_name in set_names:
            ext_settings = settings.extensions[set_name]
            insn_names = ext_settings.instructions
            if insn_names is None:
                logger.warning("Skipping empty set %s", set_name)
                continue
            assert len(insn_names) > 0, f"No instructions found in set: {set_name}"
            sub = ext_settings.model
            if sub != input_model:
                continue
            # TODO: populate model in yaml backend!
            if sub is None:  # Fallbacke
                sub = set_name
            for insn_name in insn_names:
                ll_file = settings.temp_dir / sub / set_name / f"{insn_name}.ll"
                if not ll_file.is_file():
                    logger.warning("Skipping %s due to errors.", insn_name)
                    continue
                output_file = ll_file.parent / (ll_file.stem + ".gmir")
                name = ll_file.name
                logger.info("Writing gmir for %s", name)
                try:
                    # TODO: move to backends
                    cdsl2llvm_build_dir = None
                    integrated_pattern_gen = settings.tools.pattern_gen.integrated
                    if integrated_pattern_gen:
                        config = settings.llvm.default_config
                        cdsl2llvm_build_dir = str(settings.build_dir / config)
                    else:
                        cdsl2llvm_build_dir = str(settings.deps_dir / "cdsl2llvm" / "llvm" / "build")
                    mattr = default_mattr
                    if ext_settings is not None:
                        # predicate = ext_settings.get_predicate(name=set_name)
                        arch_ = ext_settings.get_arch(name=set_name)
                        mattr = ",".join([*mattr.split(","), f"+{arch_}"])
                    # TODO: migrate with pass to cmdline backend
                    cdsl2llvm.convert_ll_to_gmir(
                        # settings.deps_dir / "cdsl2llvm" / "llvm" / "build", ll_file, output_file
                        cdsl2llvm_build_dir,
                        ll_file,
                        output_file,
                        mattr=mattr,
                        xlen=xlen,
                    )
                except AssertionError:
                    pass
                    # errs.append((insn_name, str(ex)))
    if len(errs) > 0:
        # print("errs", errs)
        for insn_name, err_str in errs:
            print("Err:", insn_name, err_str)
            input("!")


def gen_seal5_td(
    input_model: str,
    settings: Optional[Seal5Settings] = None,
    env: Optional[dict] = None,
    verbose: bool = False,
    **kwargs,
):
    assert input_model is None
    patch_name = "seal5_td"
    dest = "llvm/lib/Target/RISCV/seal5.td"
    dest2 = "llvm/lib/Target/RISCV/RISCV.td"
    content = """
// Includes
// seal5.td - seal5_td_includes - INSERTION_START
// seal5.td - seal5_td_includes - INSERTION_END
"""
    content2 = """
include "seal5.td"
"""

    file_artifact = File(
        dest,
        content=content,
    )
    patch_artifact = NamedPatch(
        dest2,
        key="riscv_td_includes",
        content=content2,
    )
    artifacts = [file_artifact, patch_artifact]

    index_file = settings.temp_dir / "seal5_td_index.yml"
    write_index_yaml(index_file, artifacts, {}, content=True)
    patch_settings = PatchSettings(
        name=patch_name,
        stage=int(PatchStage.PHASE_1),
        comment="Add seal5.td to llvm/lib/Target/RISCV",
        index=str(index_file),
        generated=True,
        target="llvm",
    )
    settings.add_patch(patch_settings)


def gen_model_td(
    input_model: str,
    settings: Optional[Seal5Settings] = None,
    env: Optional[dict] = None,
    verbose: bool = False,
    **kwargs,
):
    assert input_model is not None
    patch_name = f"model_td_{input_model}"
    dest = f"llvm/lib/Target/RISCV/seal5/{input_model}.td"
    dest2 = "llvm/lib/Target/RISCV/seal5.td"
    content = f"""
// Includes
// {input_model}.td - {input_model.lower()}_td_includes - INSERTION_START
// {input_model}.td - {input_model.lower()}_td_includes - INSERTION_END
"""
    content2 = f"""
include "seal5/{input_model}.td"
"""

    file_artifact = File(
        dest,
        content=content,
    )
    patch_artifact = NamedPatch(
        dest2,
        key=f"{input_model.lower()}_td_includes",
        content=content2,
    )
    artifacts = [file_artifact, patch_artifact]

    index_file = settings.temp_dir / "model_td_index.yml"
    write_index_yaml(index_file, artifacts, {}, content=True)
    patch_settings = PatchSettings(
        name=patch_name,
        stage=int(PatchStage.PHASE_1),
        comment=f"Add {input_model}.td to llvm/lib/Target/RISCV/seal5",
        index=str(index_file),
        generated=True,
        target="llvm",
    )
    settings.add_patch(patch_settings)


def gen_set_td(
    input_model: str,
    settings: Optional[Seal5Settings] = None,
    env: Optional[dict] = None,
    verbose: bool = False,
    **kwargs,
):
    assert input_model is not None
    artifacts = []
    includes = []
    for set_name, set_settings in settings.extensions.items():
        if set_settings.model != input_model:
            continue
        set_name_lower = set_name.lower()
        patch_name = f"set_td_{set_name}"
        dest = f"llvm/lib/Target/RISCV/seal5/{set_name}.td"
        content = f"""
// Includes
// {set_name}.td - {set_name_lower}_set_td_includes - INSERTION_START
// {set_name}.td - {set_name_lower}_set_td_includes - INSERTION_END
"""
        includes.append(f"seal5/{set_name}.td")
        file_artifact = File(
            dest,
            content=content,
        )
        artifacts.append(file_artifact)
    content2 = f"// {input_model}\n" + "\n".join([f'include "{inc}"' for inc in includes]) + "\n"
    dest2 = "llvm/lib/Target/RISCV/seal5.td"
    patch_artifact = NamedPatch(
        dest2,
        key="seal5_td_includes",
        content=content2.strip(),
    )
    artifacts.append(patch_artifact)

    index_file = settings.temp_dir / f"{input_model}_set_td_index.yml"
    write_index_yaml(index_file, artifacts, {}, content=True)
    patch_name = f"set_td_{input_model}"
    patch_settings = PatchSettings(
        name=patch_name,
        stage=int(PatchStage.PHASE_1),
        comment=f"Add {input_model} set includes to llvm/lib/Target/RISCV/seal5",
        index=str(index_file),
        generated=True,
        target="llvm",
    )
    settings.add_patch(patch_settings)


def pattern_gen_pass(
    model_name: str,
    settings: Optional[Seal5Settings] = None,
    env: Optional[dict] = None,
    verbose: bool = False,
    split: bool = True,
    **kwargs,
):
    assert settings is not None, "Pass needs settings."
    llvm_version = settings.llvm.state.version
    assert llvm_version is not None
    if llvm_version.major < 18:
        raise RuntimeError("PatternGen needs LLVM version 18 or higher")
    PATTERN_GEN_PASSES = [
        ("write_cdsl_compat", write_cdsl, {"split": split, "compat": True}),
        ("behav_to_llvmir", convert_behav_to_llvmir, {"split": split}),
        ("llvmir_to_gmir", convert_llvmir_to_gmir, {"split": split}),
        # ("write_fmt", convert_behav_to_tablegen, {"split": split, "formats": True, "patterns": False}),
        ("behav_to_pat", convert_behav_to_tablegen, {"split": split, "formats": False, "patterns": True}),
    ]
    pass_list = []
    for pass_name, pass_handler, pass_options in PATTERN_GEN_PASSES:
        pass_list.append(Seal5Pass(pass_name, PassType.GENERATE, PassScope.MODEL, pass_handler, options=pass_options))
    # TODO: get parent pass context automatically
    parent = kwargs.get("parent", None)
    assert parent is not None
    with PassManager("pattern_gen_passes", pass_list, skip=[], only=[], parent=parent) as pm:
        result = pm.run([model_name], settings=settings, env=env, verbose=verbose)
    return result
