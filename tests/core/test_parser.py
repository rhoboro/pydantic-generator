from pathlib import Path


def test_json_parser():
    from pydantic_generator.core.parser import JsonParser
    with open(Path(__file__).parent.parent / 'data' / 'data_01.json') as reader:
        parser = JsonParser("Response", reader)

        expected = []
        actual = parser.parse()
        assert expected == actual
