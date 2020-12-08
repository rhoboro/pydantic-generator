import ast
import json
from ast import *
from datetime import datetime
from typing import IO, Iterable, Union

from .base import Parser

JsonValue = Union[dict, list, int, str, datetime]


class JsonParser(Parser):
    def __init__(self, name: str, reader: IO) -> None:
        self.name = name
        self.body = json.load(reader)

    def parse(self) -> Iterable[ast.ClassDef]:
        return list(class_parse(self.name, self.body))


def class_parse(key: str, json_value: dict) -> Iterable[ast.ClassDef]:
    return []
    print(key, json_value)
    for k, v in json_value.items():
        if isinstance(v, dict):
            yield ast.ClassDef(
                name=key,
                bases=[Name(id="BaseModel", ctx=Load())],
                keywords=[],
                body=list(class_parse(k, v)),
                decorator_list=[],
            )
        elif isinstance(v, list):
            if v:
                if isinstance(v[0], dict):
                    yield from class_parse(k, v[0])
                elif isinstance(v[0], (int, str)):
                    yield AnnAssign(
                        target=Name(id=k, ctx=Store()),
                        annotation=Subscript(
                            value=Attribute(
                                value=Name(id="List", ctx=Load()),
                                # value=Name(id="typing", ctx=Load()), attr="List", ctx=Load()
                            ),
                            slice=Name(id=v[0].__class__.__name__, ctx=Load()),
                            ctx=Load(),
                        ),
                        simple=1,
                    )
            else:
                yield ClassDef(
                    name=key,
                    bases=[Name(id="BaseModel", ctx=Load())],
                    keywords=[],
                    body=[
                        AnnAssign(
                            target=Name(id=k, ctx=Store()),
                            annotation=Subscript(
                                value=Attribute(
                                    # value=Name(id="typing", ctx=Load()), attr="List", ctx=Load()
                                    value=Name(id="List", ctx=Load()),
                                ),
                                slice=Name(id="int", ctx=Load()),
                                ctx=Load(),
                            ),
                            simple=1,
                        )
                    ],
                    decorator_list=[],
                )
        elif isinstance(v, (int, str)):
            yield AnnAssign(
                target=Name(id=k, ctx=Store()),
                annotation=Name(id=v.__class__.__name__, ctx=Load()),
                simple=1,
            )
