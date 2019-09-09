import pytest

from tartiflette import TartifletteError
from tartiflette.language.ast import Location
from tartiflette.language.parsers.lark import parse_to_document
from tartiflette.schema.transformer import schema_from_sdl
from tartiflette.validation.rules import UniqueTypeNamesRule
from tartiflette.validation.validate import validate_sdl


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "old_sdl,new_sdl,expected",
    [
        (
            None,
            """
            directive @test on SCHEMA
            """,
            [],
        ),
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
            type Bar
            type Baz
            """,
            [],
        ),
        # Reason: lark parser doesn't implements the query language grammar
        # (
        #     None,
        #     """
        #     query Foo { __typename }
        #     fragment Foo on Query { __typename }
        #     directive @Foo on SCHEMA
        #
        #     type Foo
        #     """,
        #     [],
        # ),
        (
            None,
            """
            type Foo

            scalar Foo
            type Foo
            interface Foo
            union Foo
            enum Foo
            input Foo
            """,
            [
                TartifletteError(
                    message="There can be only one type named < Foo >.",
                    locations=[
                        Location(line=2, column=18, line_end=2, column_end=21),
                        Location(line=4, column=20, line_end=4, column_end=23),
                    ],
                ),
                TartifletteError(
                    message="There can be only one type named < Foo >.",
                    locations=[
                        Location(line=2, column=18, line_end=2, column_end=21),
                        Location(line=5, column=18, line_end=5, column_end=21),
                    ],
                ),
                TartifletteError(
                    message="There can be only one type named < Foo >.",
                    locations=[
                        Location(line=2, column=18, line_end=2, column_end=21),
                        Location(line=6, column=23, line_end=6, column_end=26),
                    ],
                ),
                TartifletteError(
                    message="There can be only one type named < Foo >.",
                    locations=[
                        Location(line=2, column=18, line_end=2, column_end=21),
                        Location(line=7, column=19, line_end=7, column_end=22),
                    ],
                ),
                TartifletteError(
                    message="There can be only one type named < Foo >.",
                    locations=[
                        Location(line=2, column=18, line_end=2, column_end=21),
                        Location(line=8, column=18, line_end=8, column_end=21),
                    ],
                ),
                TartifletteError(
                    message="There can be only one type named < Foo >.",
                    locations=[
                        Location(line=2, column=18, line_end=2, column_end=21),
                        Location(line=9, column=19, line_end=9, column_end=22),
                    ],
                ),
            ],
        ),
        (
            """
            type Foo
            """,
            """
            type Bar
            """,
            [],
        ),
        (
            """
            directive @Foo on SCHEMA
            """,
            """
            type Foo
            """,
            [],
        ),
        (
            """
            type Foo
            """,
            """
            scalar Foo
            type Foo
            interface Foo
            union Foo
            enum Foo
            input Foo
            """,
            [
                TartifletteError(
                    message="Type < Foo > already exists in the schema. It cannot also be defined in this type definition.",
                    locations=[
                        Location(line=2, column=20, line_end=2, column_end=23)
                    ],
                ),
                TartifletteError(
                    message="Type < Foo > already exists in the schema. It cannot also be defined in this type definition.",
                    locations=[
                        Location(line=3, column=18, line_end=3, column_end=21)
                    ],
                ),
                TartifletteError(
                    message="Type < Foo > already exists in the schema. It cannot also be defined in this type definition.",
                    locations=[
                        Location(line=4, column=23, line_end=4, column_end=26)
                    ],
                ),
                TartifletteError(
                    message="Type < Foo > already exists in the schema. It cannot also be defined in this type definition.",
                    locations=[
                        Location(line=5, column=19, line_end=5, column_end=22)
                    ],
                ),
                TartifletteError(
                    message="Type < Foo > already exists in the schema. It cannot also be defined in this type definition.",
                    locations=[
                        Location(line=6, column=18, line_end=6, column_end=21)
                    ],
                ),
                TartifletteError(
                    message="Type < Foo > already exists in the schema. It cannot also be defined in this type definition.",
                    locations=[
                        Location(line=7, column=19, line_end=7, column_end=22)
                    ],
                ),
            ],
        ),
    ],
)
async def test_unique_type_names(old_sdl, new_sdl, expected):
    old_schema = None
    if old_sdl:
        old_schema = schema_from_sdl(old_sdl, "test_unique_type_names")
        await old_schema.bake(run_validation=False)
    assert (
        validate_sdl(
            parse_to_document(new_sdl), old_schema, rules=[UniqueTypeNamesRule]
        )
        == expected
    )
