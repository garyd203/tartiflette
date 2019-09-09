import pytest

from tartiflette import TartifletteError
from tartiflette.language.ast import Location
from tartiflette.language.parsers.lark import parse_to_document
from tartiflette.schema.transformer import schema_from_sdl
from tartiflette.validation.rules import UniqueDirectiveNamesRule
from tartiflette.validation.validate import validate_sdl


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "old_sdl,new_sdl,expected",
    [
        (
            None,
            """
            type Foo
            """,
            [],
        ),
        (
            None,
            """
            directive @foo on SCHEMA
            """,
            [],
        ),
        (
            None,
            """
            directive @foo on SCHEMA
            directive @bar on SCHEMA
            directive @baz on SCHEMA
            """,
            [],
        ),
        (
            None,
            """
            type foo

            directive @foo on SCHEMA
            """,
            [],
        ),
        (
            None,
            """
            directive @foo on SCHEMA

            directive @foo on SCHEMA
            """,
            [
                TartifletteError(
                    message="There can be only one directive named < foo >.",
                    locations=[
                        Location(line=2, column=24, line_end=2, column_end=27),
                        Location(line=4, column=24, line_end=4, column_end=27),
                    ],
                )
            ],
        ),
        (
            None,
            """
            directive @foo on SCHEMA

            directive @foo on SCHEMA
            directive @foo on SCHEMA
            """,
            [
                TartifletteError(
                    message="There can be only one directive named < foo >.",
                    locations=[
                        Location(line=2, column=24, line_end=2, column_end=27),
                        Location(line=4, column=24, line_end=4, column_end=27),
                    ],
                ),
                TartifletteError(
                    message="There can be only one directive named < foo >.",
                    locations=[
                        Location(line=2, column=24, line_end=2, column_end=27),
                        Location(line=5, column=24, line_end=5, column_end=27),
                    ],
                ),
            ],
        ),
        (
            """
            directive @foo on SCHEMA
            """,
            """
            directive @bar on SCHEMA
            """,
            [],
        ),
        (
            """
            type foo
            """,
            """
            directive @skip on SCHEMA
            """,
            [],
        ),
        (
            """
            type foo
            """,
            """
            directive @foo on SCHEMA
            """,
            [],
        ),
        (
            """
            directive @foo on SCHEMA
            """,
            """
            directive @foo on SCHEMA
            """,
            [
                TartifletteError(
                    message="Directive < foo > already exists in the schema. It cannot be redefined.",
                    locations=[
                        Location(line=2, column=24, line_end=2, column_end=27)
                    ],
                )
            ],
        ),
        (
            """
            directive @foo on SCHEMA
            """,
            """
            directive @foo on SCHEMA
            directive @foo on SCHEMA
            """,
            [
                TartifletteError(
                    message="Directive < foo > already exists in the schema. It cannot be redefined.",
                    locations=[
                        Location(line=2, column=24, line_end=2, column_end=27)
                    ],
                ),
                TartifletteError(
                    message="Directive < foo > already exists in the schema. It cannot be redefined.",
                    locations=[
                        Location(line=3, column=24, line_end=3, column_end=27)
                    ],
                ),
            ],
        ),
    ],
)
async def test_unique_directive_names(old_sdl, new_sdl, expected):
    old_schema = None
    if old_sdl:
        old_schema = schema_from_sdl(old_sdl, "test_unique_directive_names")
        await old_schema.bake(run_validation=False)
    assert (
        validate_sdl(
            parse_to_document(new_sdl),
            old_schema,
            rules=[UniqueDirectiveNamesRule],
        )
        == expected
    )
