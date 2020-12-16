import ast
import json
from pathlib import Path

import pytest

PARAMS = [
    ("data_01.json", "data_01.py"),
]


@pytest.mark.parametrize("json_file, expected_data", PARAMS)
def test_json_parser(json_file, expected_data):
    from pydantic_generator.core.parser import JsonParser

    with open(Path(__file__).parent.parent / "data" / json_file) as reader:
        ast_ = list(JsonParser("Response", reader).parse())[0]
        actual = ast.unparse(ast_)
        print(actual)
        expected = open(Path(__file__).parent.parent / "data" / expected_data).read()
        assert expected == actual


def test_transform():
    from pydantic_generator.core.parser.json_parser import NLIJson

    with open(Path(__file__).parent.parent / "data" / "data_01.json") as reader:
        target = json.load(reader)
        nli = NLIJson(target)
        expected = {
            "glossary": {
                "title": ["example glossary"],
                "GlossDiv": {
                    "title": ["S"],
                    "GlossList": {
                        "GlossEntry": {
                            "ID": ["SGML"],
                            "SortAs": ["SGML"],
                            "GlossTerm": ["Standard Generalized Markup Language"],
                            "Acronym": ["SGML"],
                            "Abbrev": ["ISO 8879:1986"],
                            "GlossDef": {
                                "para": [
                                    "A meta-markup language, used to create markup languages such as DocBook."
                                ],
                                "__pyg_length_GlossSeeAlso[]": [2],
                                "GlossSeeAlso[]": ["GML", "XML"],
                            },
                            "GlossSee": ["markup"],
                        }
                    },
                },
            }
        }
        print(nli.data)
        assert expected == nli.data
