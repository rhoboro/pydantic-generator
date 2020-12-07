import ast
import json
from typing import Iterable


class Parser:
    def parse(self) -> Iterable[ast.AST]:
        return [ast.parse("")]


class JsonParser(Parser):
    def __init__(self, reader) -> None:
        self.body = json.load(reader)
