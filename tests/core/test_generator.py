from io import StringIO


def test_pydanticgen():
    from pydantic_generator.core.generator import pydanticgen, ModuleNode

    reader = StringIO("{}")
    actual = pydanticgen("Response", reader)

    assert isinstance(actual, ModuleNode)
