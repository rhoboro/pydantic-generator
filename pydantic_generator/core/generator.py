import ast
from enum import Enum, auto
from itertools import chain
from typing import IO, Any, Iterable, Union

from .parser import JsonParser

USE_TYPING_LIST = False

TYPING_NAME = (
    "Any",
    "List",
    "Optional",
)


class Kind(Enum):
    JSON = auto


class ModuleNode:
    class ImportCollector(ast.NodeVisitor):
        def __init__(self):
            self.import_names = set()

        def visit_Name(self, node: ast.AST) -> Any:
            if USE_TYPING_LIST and node.id == "list":
                node.id = "List"

            if node.id in TYPING_NAME:
                self.import_names.add(node.id)
            return node

    def __init__(self, nodes: Iterable[ast.ClassDef]):
        self.tree = ast.Module(
            body=list(chain(self.collect_imports(nodes), nodes)), type_ignores=[]
        )

    def unparse(self) -> str:
        return ast.unparse(ast.fix_missing_locations(self.tree))

    @property
    def first_class_name(self) -> str:
        for node in self.tree.body:
            if isinstance(node, ast.ClassDef):
                return node.name

        raise RuntimeError("Not initialized")

    def collect_imports(
        self, nodes: Iterable[ast.ClassDef]
    ) -> Iterable[Union[ast.Import, ast.ImportFrom]]:
        collector = self.ImportCollector()
        for node in nodes:
            collector.visit(node)

        imports = []
        if collector.import_names:
            # 標準ライブラリを先にインポート
            imports.append(
                ast.ImportFrom(
                    module="typing",
                    names=[ast.alias(name=name) for name in sorted(collector.import_names)],
                    level=0,
                ),
            )
        imports.append(
            ast.ImportFrom(module="pydantic", names=[ast.alias(name="BaseModel")], level=0)
        )
        return imports


def pydanticgen(name: str, reader: IO, kind: Kind = Kind.JSON) -> ModuleNode:
    if kind == Kind.JSON:
        parser = JsonParser(name, reader)
    else:
        raise NotImplementedError(f"{kind} is not implemented yet.")

    return ModuleNode(parser.parse())
