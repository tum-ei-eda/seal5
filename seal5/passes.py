import os
import time
import multiprocessing
from pathlib import Path
from enum import Enum, IntFlag, auto
from dataclasses import dataclass
from typing import Callable, Optional, List
from concurrent.futures import ThreadPoolExecutor

from seal5.logging import get_logger
from seal5.settings import Seal5Settings

logger = get_logger()


NUM_THREADS = int(os.environ.get("SEAL5_NUM_THREADS", multiprocessing.cpu_count()))


class PassFormat(IntFlag):
    NONE = auto()
    CDSL = auto()
    YAML = auto()
    M2ISAR = auto()
    SEAL5 = auto()
    LLVMIR = auto()
    GMIR = auto()
    SRC = auto()


class PassType(Enum):
    TRANSFORM = auto()
    GENERATE = auto()


class PassStatus(Enum):
    CREATED = auto()
    RUNNING = auto()
    FAILED = auto()
    COMPLETED = auto()
    SKIPPED = auto()


class PassScope(Enum):
    GLOBAL = auto()
    MODEL = auto()
    SET = auto()  # not supported yet
    INSTR = auto()  # not supported yet


@dataclass
class PassResult:
    metrics: Optional[dict] = None
    outputs: Optional[List[Path]] = None


def check_filter(name, skip, only):
    if skip is None:
        skip = []
    if only is None:
        only = []
    if not ((name in only or len(only) == 0) and (name not in skip or len(skip) == 0)):
        return True
    return False


class Seal5Pass:
    def __init__(self, name, pass_type, pass_scope, handler, fmt=PassFormat.NONE, order=-1, options=None):
        self.name: str = name
        self.pass_type: PassType = pass_type
        self.pass_scope: PassScope = pass_scope
        self.handler: Callable = handler
        self.fmt: PassFormat = fmt
        self.status = PassStatus.CREATED
        self.order: int = order  # not supported yet
        self.options: Optional[dict] = options
        self.metrics: dict = {}

    def __repr__(self):
        return f"Seal5Pass({self.name}, {self.pass_type}, {self.pass_scope})"

    @property
    def is_pending(self):
        return self.status in [PassStatus.CREATED, PassStatus.SKIPPED]

    def skip(self):
        self.status = PassStatus.SKIPPED

    def run(self, inputs: List[str], *args, settings: Optional[Seal5Settings] = None, **kwargs):
        logger.debug("Running pass: %s", self)
        self.status = PassStatus.RUNNING
        assert settings is not None
        passes_settings = settings.passes
        assert passes_settings is not None
        assert passes_settings.defaults is not None
        assert passes_settings.defaults.overrides is not None
        default_overrides = passes_settings.defaults.overrides.get(self.name, None)
        self.metrics["models"] = []
        try:
            kwargs_ = {**kwargs}
            if self.options:
                kwargs_.update(self.options)
            if default_overrides:
                kwargs_.update(default_overrides)
            start = time.time()
            parent = kwargs.get("parent", None)
            if parent:
                parallel = parent.parallel
            else:
                parallel = 1
            if self.pass_scope == PassScope.MODEL:
                assert passes_settings.per_model is not None

                with ThreadPoolExecutor(max_workers=parallel) as executor:
                    futures = []
                    for input_model in inputs:
                        kwargs__ = kwargs_.copy()
                        per_model = passes_settings.per_model.get(input_model, None)
                        if per_model:
                            if check_filter(self.name, per_model.skip, per_model.only):
                                logger.info("Skipped pass %s for model %s", self.name, input_model)
                                continue
                            if per_model.overrides:
                                overrides = per_model.overrides.get(self.name, None)
                                if overrides:
                                    kwargs__.update(overrides)
                        future = executor.submit(self.handler, input_model, settings=settings, **kwargs__)
                        futures.append(future)
                    results = []
                    for i, future in enumerate(futures):
                        result = future.result()
                        input_model = inputs[i]
                        if result:
                            metrics = result.metrics
                            if metrics:
                                self.metrics["models"].append({input_model: metrics})
                        results.append(result)
                    # TODO: check results (metrics?)
            elif self.pass_scope == PassScope.GLOBAL:
                input_model = None
                result = self.handler(input_model, settings=settings, **kwargs_)
                if result:
                    metrics = result.metrics
                    if metrics:
                        self.metrics["models"].append({input_model: metrics})
            else:
                raise NotImplementedError
            end = time.time()
            diff = end - start
            self.status = PassStatus.COMPLETED
            self.metrics["time_s"] = diff
        except Exception as e:
            self.status = PassStatus.FAILED
            raise e
        return PassResult(metrics=self.metrics)


class PassManager:
    def __init__(
        self,
        name: str,
        pass_list: List[Seal5Pass],
        skip: Optional[List[str]] = None,
        only: Optional[List[str]] = None,
        parent: Optional["PassManager"] = None,
        parallel: Optional[int] = None,
    ):
        self.name = name
        self.pass_list = pass_list
        self.skip = skip if skip is not None else (parent.skip if parent else [])
        self.only = only if only is not None else (parent.only if parent else [])
        self.parallel = parallel if parallel is not None else (parent.parallel if parent else NUM_THREADS)
        self.metrics: dict = {}
        self.open: bool = False

    @property
    def size(self):
        return len(self.pass_list)

    def __enter__(self):
        assert not self.open
        self.open = True
        logger.debug("Processing %d passes...", self.size)
        return self

    def __exit__(self, *exc):
        self.open = False
        logger.debug("Done.")
        # return False

    def run(
        self,
        input_models: List[str],
        settings: Optional[Seal5Settings] = None,
        env: Optional[dict] = None,
        verbose: bool = False,
    ):
        assert self.open, "PassManager needs context"
        start = time.time()
        self.metrics["passes"] = []
        # passes_settings = settings.passes
        # assert passes_settings is not None
        # assert passes_settings.per_model is not None

        for pass_ in self.pass_list:
            # input_models_ = []
            # for model_name in input_models:
            #    overrides = passes_settings.per_model.get(model_name, None)
            #    if overrides:
            if check_filter(pass_.name, self.skip, self.only):
                pass_.skip()
                continue
            assert pass_.is_pending, f"Pass {pass_.name} is not pending"
            result = pass_.run(input_models, settings=settings, env=env, verbose=verbose, parent=self)
            if result:
                metrics = result.metrics
                if metrics:
                    self.metrics["passes"].append({pass_.name: metrics})
        end = time.time()
        diff = end - start
        self.metrics["time_s"] = diff
        return PassResult(metrics=self.metrics)


def filter_passes(
    passes: List[Seal5Pass],
    pass_name: Optional[str] = None,
    pass_type: Optional[PassType] = None,
    pass_scope: Optional[PassScope] = None,
):
    # TODO: support regex patters in name
    ret = []
    for pass_ in passes:
        if pass_name is not None:
            if pass_.name != pass_name:
                continue
        if pass_type is not None:
            if pass_.pass_type != pass_type:
                continue
        if pass_scope is not None:
            if pass_.pass_scope != pass_scope:
                continue
        ret.append(pass_)
    return ret
