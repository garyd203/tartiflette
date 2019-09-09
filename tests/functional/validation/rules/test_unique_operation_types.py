import pytest

from tartiflette import TartifletteError
from tartiflette.language.ast import Location
from tartiflette.language.parsers.lark import parse_to_document
from tartiflette.schema.transformer import schema_from_sdl
from tartiflette.validation.rules import UniqueOperationTypesRule
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
            type Foo

            schema {
              query: Foo
              mutation: Foo
              subscription: Foo
            }
            """,
            [],
        ),
        (
            None,
            """
            type Foo

            schema { query: Foo }

            extend schema {
              mutation: Foo
              subscription: Foo
            }
            """,
            [],
        ),
        (
            None,
            """
            type Foo

            schema { query: Foo }
            extend schema { mutation: Foo }
            extend schema { subscription: Foo }
            """,
            [],
        ),
        (
            None,
            """
            type Foo

            extend schema { mutation: Foo }
            extend schema { subscription: Foo }

            schema { query: Foo }
            """,
            [],
        ),
        (
            None,
            """
            type Foo

            schema {
              query: Foo
              mutation: Foo
              subscription: Foo

              query: Foo
              mutation: Foo
              subscription: Foo
            }
            """,
            [
                TartifletteError(
                    message="There can be only one < query > type in schema.",
                    locations=[
                        Location(line=5, column=15, line_end=5, column_end=25),
                        Location(line=9, column=15, line_end=9, column_end=25),
                    ],
                ),
                TartifletteError(
                    message="There can be only one < mutation > type in schema.",
                    locations=[
                        Location(line=6, column=15, line_end=6, column_end=28),
                        Location(
                            line=10, column=15, line_end=10, column_end=28
                        ),
                    ],
                ),
                TartifletteError(
                    message="There can be only one < subscription > type in schema.",
                    locations=[
                        Location(line=7, column=15, line_end=7, column_end=32),
                        Location(
                            line=11, column=15, line_end=11, column_end=32
                        ),
                    ],
                ),
            ],
        ),
        (
            None,
            """
            type Foo

            schema {
              query: Foo
              mutation: Foo
              subscription: Foo
            }

            extend schema {
              query: Foo
              mutation: Foo
              subscription: Foo
            }
            """,
            [
                TartifletteError(
                    message="There can be only one < query > type in schema.",
                    locations=[
                        Location(line=5, column=15, line_end=5, column_end=25),
                        Location(
                            line=11, column=15, line_end=11, column_end=25
                        ),
                    ],
                ),
                TartifletteError(
                    message="There can be only one < mutation > type in schema.",
                    locations=[
                        Location(line=6, column=15, line_end=6, column_end=28),
                        Location(
                            line=12, column=15, line_end=12, column_end=28
                        ),
                    ],
                ),
                TartifletteError(
                    message="There can be only one < subscription > type in schema.",
                    locations=[
                        Location(line=7, column=15, line_end=7, column_end=32),
                        Location(
                            line=13, column=15, line_end=13, column_end=32
                        ),
                    ],
                ),
            ],
        ),
        (
            None,
            """
            type Foo

            schema {
              query: Foo
              mutation: Foo
              subscription: Foo
            }

            extend schema {
              query: Foo
              mutation: Foo
              subscription: Foo
            }

            extend schema {
              query: Foo
              mutation: Foo
              subscription: Foo
            }
            """,
            [
                TartifletteError(
                    message="There can be only one < query > type in schema.",
                    locations=[
                        Location(line=5, column=15, line_end=5, column_end=25),
                        Location(
                            line=11, column=15, line_end=11, column_end=25
                        ),
                    ],
                ),
                TartifletteError(
                    message="There can be only one < mutation > type in schema.",
                    locations=[
                        Location(line=6, column=15, line_end=6, column_end=28),
                        Location(
                            line=12, column=15, line_end=12, column_end=28
                        ),
                    ],
                ),
                TartifletteError(
                    message="There can be only one < subscription > type in schema.",
                    locations=[
                        Location(line=7, column=15, line_end=7, column_end=32),
                        Location(
                            line=13, column=15, line_end=13, column_end=32
                        ),
                    ],
                ),
                TartifletteError(
                    message="There can be only one < query > type in schema.",
                    locations=[
                        Location(line=5, column=15, line_end=5, column_end=25),
                        Location(
                            line=17, column=15, line_end=17, column_end=25
                        ),
                    ],
                ),
                TartifletteError(
                    message="There can be only one < mutation > type in schema.",
                    locations=[
                        Location(line=6, column=15, line_end=6, column_end=28),
                        Location(
                            line=18, column=15, line_end=18, column_end=28
                        ),
                    ],
                ),
                TartifletteError(
                    message="There can be only one < subscription > type in schema.",
                    locations=[
                        Location(line=7, column=15, line_end=7, column_end=32),
                        Location(
                            line=19, column=15, line_end=19, column_end=32
                        ),
                    ],
                ),
            ],
        ),
        (
            None,
            """
            type Foo

            schema {
              query: Foo
            }

            extend schema {
              mutation: Foo
              subscription: Foo
            }

            extend schema {
              query: Foo
              mutation: Foo
              subscription: Foo
            }
            """,
            [
                TartifletteError(
                    message="There can be only one < query > type in schema.",
                    locations=[
                        Location(line=5, column=15, line_end=5, column_end=25),
                        Location(
                            line=14, column=15, line_end=14, column_end=25
                        ),
                    ],
                ),
                TartifletteError(
                    message="There can be only one < mutation > type in schema.",
                    locations=[
                        Location(line=9, column=15, line_end=9, column_end=28),
                        Location(
                            line=15, column=15, line_end=15, column_end=28
                        ),
                    ],
                ),
                TartifletteError(
                    message="There can be only one < subscription > type in schema.",
                    locations=[
                        Location(
                            line=10, column=15, line_end=10, column_end=32
                        ),
                        Location(
                            line=16, column=15, line_end=16, column_end=32
                        ),
                    ],
                ),
            ],
        ),
        (
            """
            type Foo
            """,
            """
            schema {
              query: Foo
              mutation: Foo
              subscription: Foo
            }
            """,
            [],
        ),
        (
            """
            type Foo
            """,
            """
            schema { query: Foo }
            extend schema { mutation: Foo }
            extend schema { subscription: Foo }
            """,
            [],
        ),
        (
            """
            type Query
            """,
            """
            extend schema { mutation: Foo }
            extend schema { subscription: Foo }
            """,
            [],
        ),
        (
            """
            type Query
            type Mutation
            type Subscription

            type Foo
            """,
            """
            extend schema {
              query: Foo
              mutation: Foo
              subscription: Foo
            }
            """,
            [
                TartifletteError(
                    message="Type for < query > already defined in the schema. It cannot be redefined.",
                    locations=[
                        Location(line=3, column=15, line_end=3, column_end=25)
                    ],
                ),
                TartifletteError(
                    message="Type for < mutation > already defined in the schema. It cannot be redefined.",
                    locations=[
                        Location(line=4, column=15, line_end=4, column_end=28)
                    ],
                ),
                TartifletteError(
                    message="Type for < subscription > already defined in the schema. It cannot be redefined.",
                    locations=[
                        Location(line=5, column=15, line_end=5, column_end=32)
                    ],
                ),
            ],
        ),
        (
            """
            type Query
            type Mutation
            type Subscription
            """,
            """
            extend schema {
              query: Foo
              mutation: Foo
              subscription: Foo
            }

            extend schema {
              query: Foo
              mutation: Foo
              subscription: Foo
            }
            """,
            [
                TartifletteError(
                    message="Type for < query > already defined in the schema. It cannot be redefined.",
                    locations=[
                        Location(line=3, column=15, line_end=3, column_end=25)
                    ],
                ),
                TartifletteError(
                    message="Type for < mutation > already defined in the schema. It cannot be redefined.",
                    locations=[
                        Location(line=4, column=15, line_end=4, column_end=28)
                    ],
                ),
                TartifletteError(
                    message="Type for < subscription > already defined in the schema. It cannot be redefined.",
                    locations=[
                        Location(line=5, column=15, line_end=5, column_end=32)
                    ],
                ),
                TartifletteError(
                    message="Type for < query > already defined in the schema. It cannot be redefined.",
                    locations=[
                        Location(line=9, column=15, line_end=9, column_end=25)
                    ],
                ),
                TartifletteError(
                    message="Type for < mutation > already defined in the schema. It cannot be redefined.",
                    locations=[
                        Location(
                            line=10, column=15, line_end=10, column_end=28
                        )
                    ],
                ),
                TartifletteError(
                    message="Type for < subscription > already defined in the schema. It cannot be redefined.",
                    locations=[
                        Location(
                            line=11, column=15, line_end=11, column_end=32
                        )
                    ],
                ),
            ],
        ),
    ],
)
async def test_unique_operation_types(old_sdl, new_sdl, expected):
    old_schema = None
    if old_sdl:
        old_schema = schema_from_sdl(old_sdl, "test_unique_operation_types")
        await old_schema.bake(run_validation=False)
    assert (
        validate_sdl(
            parse_to_document(new_sdl),
            old_schema,
            rules=[UniqueOperationTypesRule],
        )
        == expected
    )
