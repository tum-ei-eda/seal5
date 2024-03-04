import time
from pathlib import Path
from enum import Enum, IntFlag, auto
from dataclasses import dataclass
from typing import Callable, Optional, List
from concurrent.futures import ThreadPoolExecutor

from seal5.logging import get_logger

logger = get_logger()


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


class Seal5Pass:
    def __init__(self, name, pass_type, pass_scope, handler, order=-1, options=None):
        self.name: str = name
        self.pass_type: PassType = pass_type
        self.pass_scope: PassScope = pass_scope
        self.handler: Callable = handler
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

    def run(self, inputs: List[str], *args, **kwargs):
        logger.debug("Running pass: %s", self)
        self.status = PassStatus.RUNNING
        self.metrics["models"] = []
        try:
            kwargs_ = {**kwargs}
            if self.options:
                kwargs_.update(self.options)
            start = time.time()
            parent = kwargs.get("parent", None)
            if parent:
                parallel = parent.parallel
            else:
                parallel = 1
            if self.pass_scope == PassScope.MODEL:
                with ThreadPoolExecutor(max_workers=parallel) as executor:
                    futures = []
                    for input_model in inputs:
                        future = executor.submit(self.handler, input_model, **kwargs_)
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
                input_model = "Seal5"
                result = self.handler(input_model, **kwargs_)
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
        parallel: int = 2,
    ):
        self.name = name
        self.pass_list = pass_list
        self.skip = skip if skip is not None else []
        self.only = only if only is not None else []
        self.parallel = parallel
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

    def run(self, input_models: List[str], verbose: bool = False):
        assert self.open, "PassManager needs context"
        start = time.time()
        self.metrics["passes"] = []
        for pass_ in self.pass_list:
            if not (
                (pass_.name in self.only or len(self.only) == 0)
                and (pass_.name not in self.skip or len(self.skip) == 0)
            ):
                pass_.skip()
                continue
            assert pass_.is_pending, f"Pass {pass_.name} is not pending"
            result = pass_.run(input_models, verbose=verbose, parent=self)
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
