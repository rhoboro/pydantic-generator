import ast
import json
from ast import *
from typing import IO, Iterable, Tuple, Union

from .base import Parser

# Supported types in https://docs.python.org/ja/3/library/json.html#json.JSONEncoder
JsonValue = Union[dict, list, int, float, str, bool, None]


class JsonParser(Parser):
    def __init__(self, name: str, reader: IO) -> None:
        self.name = name
        self.body = json.load(reader)

    def parse(self) -> Iterable[ast.ClassDef]:
        return list(class_parse(self.name, self.body))


def class_parse(key: str, json_value: JsonValue) -> Iterable[ast.ClassDef]:
    if isinstance(json_value, dict):
        yield ast.ClassDef(
            name=key.capitalize(),
            bases=[Name(id="BaseModel", ctx=Load())],
            keywords=[],
            body=list(list(class_parse(k, v)) for k, v in json_value.items()),
            decorator_list=[],
        )
        yield AnnAssign(
            target=Name(id=key, ctx=Store()),
            annotation=Name(id=key.capitalize(), ctx=Load()),
            simple=1,
        )
    elif isinstance(json_value, list):
        if json_value:
            if isinstance(json_value[0], dict):
                yield ast.ClassDef(
                    name=key.capitalize(),
                    bases=[Name(id="BaseModel", ctx=Load())],
                    keywords=[],
                    body=list(list(class_parse(k, v)) for k, v in json_value[0].items()),
                    decorator_list=[],
                )
                yield AnnAssign(
                    target=Name(id=key, ctx=Store()),
                    annotation=Subscript(
                        value=Name(id="list", ctx=Load()),
                        slice=Name(id=key.capitalize(), ctx=Load()),
                        ctx=Load(),
                    ),
                    simple=1,
                )
            elif isinstance(json_value[0], list):
                value, nest = detect(json_value[0])
                if isinstance(value, dict):
                    yield ast.ClassDef(
                        name=key.capitalize(),
                        bases=[Name(id="BaseModel", ctx=Load())],
                        keywords=[],
                        body=list(list(class_parse(k, v)) for k, v in value.items()),
                        decorator_list=[],
                    )
                    yield AnnAssign(
                        target=Name(id=key, ctx=Store()),
                        annotation=nested_element(key, key.capitalize(), nest),
                        simple=1,
                    )
                elif isinstance(value, list):
                    yield AnnAssign(
                        target=Name(id=key, ctx=Store()),
                        annotation=nested_element(key, list.__name__, nest),
                        simple=1,
                    )

                elif isinstance(value, (bool, int, float, str)):
                    yield AnnAssign(
                        target=Name(id=key, ctx=Store()),
                        annotation=nested_element(key, value.__class__.__name__, nest),
                        simple=1,
                    )

            elif isinstance(json_value[0], (bool, int, float, str)):
                yield AnnAssign(
                    target=Name(id=key, ctx=Store()),
                    annotation=Subscript(
                        value=Name(id="list", ctx=Load()),
                        slice=Name(id=json_value[0].__class__.__name__, ctx=Load()),
                        ctx=Load(),
                    ),
                    simple=1,
                )
        else:
            yield AnnAssign(
                target=Name(id=key, ctx=Store()), annotation=Name(id="list", ctx=Load()), simple=1
            )

    elif isinstance(json_value, (bool, int, float, str)):
        yield AnnAssign(
            target=Name(id=key, ctx=Store()),
            annotation=Name(id=json_value.__class__.__name__, ctx=Load()),
            simple=1,
        )


def detect(value: JsonValue, nest: int = 0) -> Tuple[JsonValue, int]:
    if not isinstance(value, list):
        return value, nest
    else:
        if value:
            return detect(value[0], nest + 1)
        else:
            return value, nest


def nested_element(key: str, type_name: str, nest: int) -> Subscript:
    if nest:
        return Subscript(
            value=Name(id="list", ctx=Load()),
            slice=nested_element(key, type_name, nest - 1),
            ctx=Load(),
        )
    else:
        return Subscript(
            value=Name(id="list", ctx=Load()),
            slice=Name(id=type_name, ctx=Load()),
            ctx=Load(),
        )
