from enum import Enum, auto
from typing import Callable, Optional, List


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


class Seal5Pass:
    def __init__(self, name, pass_type, pass_scope, handler, order=-1, options=None):
        self.name: str = name
        self.pass_type: PassType = pass_type
        self.pass_scope: PassScope = pass_scope
        self.handler: Callable = handler
        self.status = PassStatus.CREATED
        self.order: int = order  # not supported yet
        self.options: Optional[dict] = options

    @property
    def is_pending(self):
        return self.status in [PassStatus.CREATED, PassStatus.SKIPPED]

    def skip(self):
        self.status = PassStatus.SKIPPED

    def run(self, *args, **kwargs):
        self.status = PassStatus.RUNNING
        try:
            kwargs_ = {**kwargs}
            if self.options:
                kwargs_.update(self.options)
            self.handler(*args, **kwargs_)
            self.status = PassStatus.COMPLETED
        except Exception as e:
            self.status = PassStatus.FAILED
            raise e


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
