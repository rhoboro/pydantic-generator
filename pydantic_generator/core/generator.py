import ast
from enum import Enum, auto
from itertools import chain
from typing import IO, Iterable, Union

from .parser import JsonParser


class Kind(Enum):
    JSON = auto


class ModelSchema:
    def __init__(self, nodes: Iterable[ast.ClassDef]):
        self.tree = ast.Module(
            body=list(chain(self.collect_imports(nodes), nodes)), type_ignores=[]
        )

    def to_string(self) -> str:
        return ast.unparse(ast.fix_missing_locations(self.tree))

    @property
    def first_model_name(self) -> str:
        for node in self.tree.body:
            if isinstance(node, ast.ClassDef):
                return node.name

        raise RuntimeError("Not initialized")

    def collect_imports(
        self, nodes: Iterable[ast.ClassDef]
    ) -> Iterable[Union[ast.Import, ast.ImportFrom]]:
        return [ast.ImportFrom(module="pydantic", names=[ast.alias(name="BaseModel")], level=0)]


def pydanticgen(name: str, reader: IO, kind: Kind = Kind.JSON) -> ModelSchema:
    if kind == Kind.JSON:
        parser = JsonParser(name, reader)
    else:
        raise NotImplementedError(f"{kind} is not implemented yet.")

    return ModelSchema(parser.parse())
