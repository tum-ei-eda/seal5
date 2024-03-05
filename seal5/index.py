from typing import List, Dict, Optional
from pathlib import Path
import yaml


class Artifact:
    def __init__(
        self, dest_path: Path, src_path: Optional[Path] = None, content: Optional[str] = None, append: bool = False
    ):
        self.dest_path: Path = dest_path
        self.src_path: Optional[Path] = src_path
        self.content: Optional[str] = content
        self.append: bool = append

    def to_dict(self, content=False) -> dict:
        return {
            key: str(value) if isinstance(value, Path) else value
            for key, value in vars(self).items()
            if content or key not in ["content"]
        }


class GitPatch(Artifact):
    def __init__(
        self,
        dest_path: Path,
        src_path: Optional[Path] = None,
        content: Optional[str] = None,
        message: Optional[str] = None,
        append: bool = False,
    ):
        super().__init__(dest_path, src_path=src_path, content=content, append=append)
        self.message = "???" if message is None else message
        # TODO: context
        raise NotImplementedError


class Patch(Artifact):
    def __init__(
        self, dest_path: Path, src_path: Optional[Path] = None, content: Optional[str] = None, append: bool = False
    ):
        super().__init__(dest_path, src_path=src_path, content=content, append=append)


class NamedPatch(Patch):
    def __init__(
        self,
        dest_path: Path,
        key: str,
        src_path: Optional[Path] = None,
        content: Optional[Path] = None,
        append: bool = False,
    ):
        super().__init__(dest_path, src_path=src_path, content=content, append=append)
        self.key: str = key
        # self.src: str = self.out_path

    # @property
    # def out_path(self):
    #     return self.path + "." + self.key


class IndexedPatch(Patch):
    def __init__(
        self,
        dest_path: Path,
        line: int,
        src_path: Optional[Path] = None,
        content: Optional[Path] = None,
        append: bool = False,
    ):
        super().__init__(dest_path, src_path=src_path, content=content, append=append)
        # 0: start of file, -1: end of file
        self.line: int = line
        raise NotImplementedError


class RangedPatch(Patch):
    def __init__(
        self,
        dest_path: Path,
        start: int,
        end: int,
        src_path: Optional[Path] = None,
        content: Optional[Path] = None,
        append: bool = False,
    ):
        super().__init__(dest_path, src_path=src_path, content=content, append=append)
        # Patch is added between matching lines
        self.start: str = start
        self.end: str = end
        raise NotImplementedError


class File(Artifact):
    def __init__(
        self, dest_path: Path, src_path: Optional[Path] = None, content: Optional[Path] = None, append: bool = False
    ):
        super().__init__(dest_path, src_path=src_path, content=content, append=append)


class Directory(Artifact):
    def __init__(
        self, dest_path: Path, src_path: Optional[Path] = None, content: Optional[Path] = None, append: bool = False
    ):
        assert content is None
        assert not append
        super().__init__(dest_path, src_path=src_path, content=content, append=append)


def write_index_yaml(
    out_path: Path, global_artifacts: List[Artifact], ext_artifacts: Dict[str, List[Artifact]], content=False
):
    extensions_yaml_data = []
    for ext, artifacts_ in ext_artifacts.items():
        extension_yaml_data = {"name": ext, "artifacts": list(map(lambda a: a.to_dict(content=content), artifacts_))}
        extensions_yaml_data.append(extension_yaml_data)
    index_yaml_data = {
        "artifacts": list(map(lambda a: a.to_dict(content=content), global_artifacts)),
        "extensions": extensions_yaml_data,
    }
    with open(out_path, "w") as f:
        yaml.safe_dump(index_yaml_data, f)
