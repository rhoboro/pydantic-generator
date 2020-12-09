import ast
import json
from ast import *
from typing import IO, Iterable, Iterator, Union

from .base import Parser

# Supported types in https://docs.python.org/ja/3/library/json.html#json.JSONEncoder
CollectionValue = Union[dict, list]
PrimitiveValue = Union[bool, int, float, str]
JsonValue = Union[CollectionValue, PrimitiveValue]


class JsonParser(Parser):
    def __init__(self, name: str, reader: IO) -> None:
        self.name = name
        self.body = json.load(reader)

    def parse(self) -> Iterable[ast.ClassDef]:
        return list(class_parse(self.name, self.body))


def class_parse(key: str, json_value: JsonValue) -> Iterator[Union[ClassDef, AnnAssign]]:
    if isinstance(json_value, dict):
        yield from process_dict(key, json_value)
    elif isinstance(json_value, list):
        yield from process_list(key, json_value)
    elif isinstance(json_value, (bool, int, float, str)):
        yield from process_primitive(key, json_value)


def nested_element(key: str, type_name: str, nest: int) -> Subscript:
    """nestの数だけlist[]を付与したast.ASTを返す"""
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


def process_dict(key: str, value: dict, nest: int = 0) -> Iterator[Union[ClassDef, AnnAssign]]:
    yield ast.ClassDef(
        name=key.capitalize(),
        bases=[Name(id="BaseModel", ctx=Load())],
        keywords=[],
        body=list(list(class_parse(k, v)) for k, v in value.items()),
        decorator_list=[],
    )

    if nest:
        yield AnnAssign(
            target=Name(id=key, ctx=Store()),
            annotation=nested_element(key, key.capitalize(), nest),
            simple=1,
        )
    else:
        yield AnnAssign(
            target=Name(id=key, ctx=Store()),
            annotation=Name(id=key.capitalize(), ctx=Load()),
            simple=1,
        )


def process_list(key: str, value: list, nest: int = 0) -> Iterable[Union[ClassDef, AnnAssign]]:
    if not value:
        yield AnnAssign(
            target=Name(id=key, ctx=Store()), annotation=Name(id="list", ctx=Load()), simple=1
        )
        raise StopIteration

    if isinstance(value[0], list):
        yield from process_list(key, value[0], nest=nest + 1)
    if isinstance(value[0], dict):
        yield from process_dict(key, value[0], nest=nest)
    elif isinstance(value[0], (bool, int, float, str)):
        yield from process_primitive(key, value[0], nest=nest)


def process_primitive(key: str, value: PrimitiveValue, nest: int = 0) -> Iterator[AnnAssign]:
    if nest:
        yield AnnAssign(
            target=Name(id=key, ctx=Store()),
            annotation=nested_element(key, value.__class__.__name__, nest),
            simple=1,
        )
    else:
        yield AnnAssign(
            target=Name(id=key, ctx=Store()),
            annotation=Name(id=value.__class__.__name__, ctx=Load()),
            simple=1,
        )
