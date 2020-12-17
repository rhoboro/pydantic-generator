import ast
import json
import re
from ast import *
from collections import UserDict, defaultdict
from copy import deepcopy
from typing import IO, Iterable, Iterator, Union

from .base import Parser

MARKER_LIST = re.compile(r"(\[\])+$")

# Supported types in https://docs.python.org/ja/3/library/json.html#json.JSONEncoder
CollectionValue = Union[dict, list]
PrimitiveValue = Union[bool, int, float, str]
JsonValue = Union[CollectionValue, PrimitiveValue]
NestedDict = lambda: defaultdict(NestedDict)
KEY_LENGTH = "__pyg_length"
ALLOW_ANY = True


class Any:
    """like typing.Any

    typing.Any は __name__ を持たないため代わりとなるクラスを用意
    """

    pass


class NLIJson(UserDict):
    """Not List Included Json

    jsonのリストオブジェクトを値のリストに変換した中間表現クラス
    """

    def __init__(self, json_value: JsonValue):
        parsed_store = defaultdict(list)
        self._parse(parsed_store, json_value)
        self.data = self._to_dict(self._transform(parsed_store))

    def _parse(self, store: dict, json_value: JsonValue, key: str = ""):
        if isinstance(json_value, dict):
            for new_key, value in json_value.items():
                self._parse(store, value, f"{key}.{new_key}")
        elif isinstance(json_value, list):
            store[f"{KEY_LENGTH}_{key}"].append(len(json_value))
            for value in json_value:
                self._parse(store, value, f"{key}[]")
        elif isinstance(json_value, (bool, int, float, str)):
            store[key].append(json_value)
        elif isinstance(json_value, type(None)):
            pass

    def _transform(self, obj):
        result = NestedDict()
        for keys, value in obj.items():
            prev = result
            for key in keys.split(".")[1:-1]:
                prev = prev[key]
            if not keys.startswith(KEY_LENGTH):
                prev[keys.split(".")[-1]] = value
            else:
                prev[f'{KEY_LENGTH}_{keys.split(".")[-1]}[]'] = value

        return result

    def _to_dict(self, obj: dict, standard_dict=None):
        if standard_dict is None:
            standard_dict = dict(obj)
        for k, v in obj.items():
            if isinstance(v, defaultdict):
                standard_dict[k] = dict(v)
                self._to_dict(v, standard_dict[k])
        return standard_dict


class JsonParser(Parser):
    def __init__(self, name: str, reader: IO) -> None:
        self.name = name
        self.nli = NLIJson(json.load(reader))

    def parse(self) -> Iterable[ast.ClassDef]:
        return list(class_parse(self.name, self.nli))[:-1]


def class_parse(
    key: str,
    json_value: Union[JsonValue, NLIJson],
    lengths: list[list[int]] = None,
) -> Iterator[Union[ClassDef, AnnAssign]]:
    if key.startswith(KEY_LENGTH):
        pass
    elif isinstance(json_value, (dict, NLIJson)):
        yield from list(process_dict(key, json_value, lengths))
    elif isinstance(json_value, list):
        yield from process_list(key, json_value, lengths)
    elif isinstance(json_value, (Any, bool, int, float, str)):
        yield from _process_primitive(key, json_value)


def process_dict(
    key: str,
    value: dict,
    lengths: list[list[int]],
) -> Iterator[Union[ClassDef, AnnAssign]]:
    if key.startswith(KEY_LENGTH):
        pass
    else:
        body = []
        for k, v in value.items():
            new_lengths = deepcopy(lengths) if lengths else []
            new_length = value.get(f"{KEY_LENGTH}_{k}")
            if new_length:
                new_lengths.append(new_length)
            body.extend(list(class_parse(k, v, new_lengths)))
        if m := MARKER_LIST.search(key):
            nests = int((len(m.group()) / 2)) - 1
            optional = is_optional_class(lengths, value)
            if optional:
                annotation = Subscript(
                    value=Name(id="Optional", ctx=Load()),
                    slice=nested_element(key.rstrip(m.group()).capitalize(), nests),
                )
            else:
                annotation = nested_element(key.rstrip(m.group()).capitalize(), nests)
            yield ast.ClassDef(
                name=key.rstrip(m.group()).capitalize(),
                bases=[Name(id="BaseModel", ctx=Load())],
                keywords=[],
                body=body,
                decorator_list=[],
            )
            yield AnnAssign(
                target=Name(id=key.rstrip(m.group()), ctx=Store()),
                annotation=annotation,
                simple=1,
            )
        else:
            yield ast.ClassDef(
                name=key.capitalize(),
                bases=[Name(id="BaseModel", ctx=Load())],
                keywords=[],
                body=body,
                decorator_list=[],
            )
            yield AnnAssign(
                target=Name(id=key, ctx=Store()),
                annotation=Name(id=key.capitalize(), ctx=Load()),
                simple=1,
            )


def is_optional_class(lengths: list[list[int]], value: dict) -> bool:
    for k, v in value.items():
        if not k.startswith(KEY_LENGTH) and isinstance(v, list):
            if len(v) != lengths[0][0]:
                return True
    return False


def nested_element(type_name: str, nests: int = 0) -> Subscript:
    """nestの数だけlist[]を付与したast.ASTを返す"""
    if nests:
        return Subscript(
            value=Name(id="list", ctx=Load()),
            slice=nested_element(type_name, nests - 1),
            ctx=Load(),
        )
    else:
        return Subscript(
            value=Name(id="list", ctx=Load()),
            slice=Name(id=type_name, ctx=Load()),
            ctx=Load(),
        )


def process_list(
    key: str, value: list, lengths: list[list[int]]
) -> Iterable[Union[ClassDef, AnnAssign]]:
    if key.startswith(KEY_LENGTH):
        pass
    else:
        if not value:
            yield AnnAssign(
                target=Name(id=key, ctx=Store()), annotation=Name(id="list", ctx=Load()), simple=1
            )
            raise StopIteration

        optional = is_optional(lengths, value)
        value_type = get_data_type(key, value)

        if value_type == list:
            yield from process_list(key, value_type, lengths)
        elif value_type == dict:
            yield from process_dict(key, value_type, lengths)
        elif value_type in (Any, bool, int, float, str):
            yield from _process_primitive(key, value_type, optional)


def is_optional(lengths: list[list[int]], value: list) -> bool:
    all_num = 1
    for x in lengths:
        if len(set(x)) != 1:
            return True
        else:
            all_num *= int(set(x).pop())

    if all_num != len(value):
        return True

    return None in value


def get_data_type(key, value: list):
    if exclude_none := set([type(x) for x in value if x is not None]):
        if len(exclude_none) == 1:
            return exclude_none.pop()

    if ALLOW_ANY:
        return Any
    else:
        raise ValueError(f"2つ以上の型がある: {key}, {value}")


def _process_primitive(
    key: str, value: PrimitiveValue, optional: bool = None
) -> Iterator[AnnAssign]:
    if m := MARKER_LIST.search(key):
        nests = int((len(m.group()) / 2)) - 1
        if optional:
            annotation = Subscript(
                value=Name(id="Optional", ctx=Load()), slice=nested_element(value.__name__, nests)
            )
        else:
            annotation = nested_element(value.__name__, nests)
        yield AnnAssign(
            target=Name(id=key.rstrip(m.group()), ctx=Store()),
            annotation=annotation,
            simple=1,
        )
    else:
        if optional:
            annotation = Subscript(
                value=Name(id="Optional", ctx=Load()), slice=Name(id=value.__name__, ctx=Load())
            )
        else:
            annotation = Name(id=value.__name__, ctx=Load())
        yield AnnAssign(
            target=Name(id=key, ctx=Store()),
            annotation=annotation,
            simple=1,
        )
