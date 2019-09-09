import pytest

from tartiflette import TartifletteError
from tartiflette.language.ast import Location
from tartiflette.language.parsers.lark import parse_to_document
from tartiflette.schema.transformer import schema_from_sdl
from tartiflette.validation.rules import LoneSchemaDefinitionRule
from tartiflette.validation.validate import validate_sdl


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "old_sdl,new_sdl,expected",
    [
        (
            None,
            """
            type Query {
              foo: String
            }
            """,
            [],
        ),
        (
            None,
            """
            type Foo {
              foo: String
            }

            schema {
              query: Foo
            }
            """,
            [],
        ),
        (
            None,
            """
            type Foo {
              foo: String
            }

            schema {
              query: Foo
            }

            schema {
              mutation: Foo
            }

            schema {
              subscription: Foo
            }
            """,
            [
                TartifletteError(
                    message="Must provide only one schema definition.",
                    locations=[
                        Location(
                            line=10, column=13, line_end=12, column_end=14
                        )
                    ],
                ),
                TartifletteError(
                    message="Must provide only one schema definition.",
                    locations=[
                        Location(
                            line=14, column=13, line_end=16, column_end=14
                        )
                    ],
                ),
            ],
        ),
        (
            """
            type Foo {
              foo: String
            }
            """,
            """
            schema {
              query: Foo
            }
            """,
            [],
        ),
        (
            """
            type Foo {
              foo: String
            }

            schema {
              query: Foo
            }
            """,
            """
            schema {
              mutation: Foo
            }
            """,
            [
                TartifletteError(
                    message="Cannot define a new schema within a schema extension.",
                    locations=[
                        Location(line=2, column=13, line_end=4, column_end=14)
                    ],
                )
            ],
        ),
        (
            """
            type Foo {
              foo: String
            }

            type Query {
              fooField: Foo
            }
            """,
            """
            schema {
              mutation: Foo
            }
            """,
            [
                TartifletteError(
                    message="Cannot define a new schema within a schema extension.",
                    locations=[
                        Location(line=2, column=13, line_end=4, column_end=14)
                    ],
                )
            ],
        ),
        (
            """
            type Foo {
              foo: String
            }

            type Query {
              fooField: Foo
            }
            """,
            """
            extend schema {
              mutation: Foo
            }
            """,
            [],
        ),
    ],
)
async def test_lone_schema_definition(old_sdl, new_sdl, expected):
    old_schema = None
    if old_sdl:
        old_schema = schema_from_sdl(old_sdl, "test_lone_schema_definition")
        await old_schema.bake(run_validation=False)
    assert (
        validate_sdl(
            parse_to_document(new_sdl),
            old_schema,
            rules=[LoneSchemaDefinitionRule],
        )
        == expected
    )
