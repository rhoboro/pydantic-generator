import ast
from enum import Enum
from typing import Iterable

from .parser import JsonParser


class Kind(Enum):
    JSON = "json"


class ModelSchema:
    def __init__(self, nodes: Iterable[ast.AST]):
        self.tree = ast.Module(body=[], type_ignores=[])

    def to_string(self) -> str:
        return ast.unparse(ast.fix_missing_locations(self.tree))

    @property
    def first_model_name(self) -> str:
        for node in self.tree.body:
            if isinstance(node, ast.ClassDef):
                return node.name

        raise RuntimeError("Not initialized")


def pydanticgen(reader, kind: Kind = Kind.JSON) -> ModelSchema:
    if kind == Kind.JSON:
        parser = JsonParser(reader)
    else:
        raise NotImplementedError(f"{kind} is not implemented yet.")

    return ModelSchema(parser.parse())
