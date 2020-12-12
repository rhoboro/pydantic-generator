import ast
import json
from pathlib import Path


def test_json_parser():
    from pydantic_generator.core.parser import JsonParser
    with open(Path(__file__).parent.parent / 'data' / 'data_01.json') as reader:
        parser = JsonParser("Response", reader)

        expected = []
        actual = parser.parse()
        print(ast.unparse(list(actual)[0]))
        assert expected == actual


def test_transform():
    from pydantic_generator.core.parser.json_parser import NLIJson
    with open(Path(__file__).parent.parent / 'data' / 'data_01.json') as reader:
        target = json.load(reader)
        nli = NLIJson(target)
        expected = {
            "__pyg_length_users": [2],
            "users[]": {
                "id": [1, 2],
                "name": ["John Doe", "Bob"],
                "signup_ts": ["2020-12-07T20:48:07.987261+09:00", "2020-12-07T20:48:07.987261+09:00"],
                "friends[]": [2, 3, 4, 2, 3, 4, 5],
                "xxx": {"yyy[3]": [1, 2, 3, 1, 2, 3], "zzz": {"a": [1, 3]}},
                "__pyg_length_friends": [3, 4]
            },
            "hoge": {"ham[1][1][3]": {"egg": [None, 1, 2], "spam": [2, 2, 3], "piyo": [3]}},
        }
        print(nli.data)
        assert expected == nli.data
        assert expected['users[2]']['xxx'] == nli['users[2]']['xxx']
