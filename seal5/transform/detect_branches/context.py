class CollectRWContext:

    def __init__(self) -> None:
        pass  # TODO: remove if not needed
        # self.reads = []
        # self.writes = []
        # self.is_read = False
        # self.is_write = False


class DAGBuilderContext(CollectRWContext):
    def __init__(self) -> None:
        super().__init__()
        self.patterns = []
        self.complex_patterns = []
