import pytest

from tartiflette import TartifletteError
from tartiflette.language.ast import Location
from tartiflette.language.parsers.lark import parse_to_document
from tartiflette.schema.transformer import schema_from_sdl
from tartiflette.validation.rules import KnownTypeNamesRule
from tartiflette.validation.validate import validate_sdl


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "old_sdl,new_sdl,expected",
    [
        (
            None,
            """
            scalar String
            scalar Int
            scalar Float
            scalar Boolean
            scalar ID

            type Query {
              string: String
              int: Int
              float: Float
              boolean: Boolean
              id: ID
            }
            """,
            [],
        ),
        (
            None,
            """
            scalar String

            union SomeUnion = SomeObject | AnotherObject

            type SomeObject implements SomeInterface {
              someScalar(arg: SomeInputObject): SomeScalar
            }

            type AnotherObject {
              foo(arg: SomeInputObject): String
            }

            type SomeInterface {
              someScalar(arg: SomeInputObject): SomeScalar
            }

            input SomeInputObject {
              someScalar: SomeScalar
            }

            scalar SomeScalar

            type RootQuery {
              someInterface: SomeInterface
              someUnion: SomeUnion
              someScalar: SomeScalar
              someObject: SomeObject
            }

            schema {
              query: RootQuery
            }
            """,
            [],
        ),
        (
            None,
            """
            type A
            type B

            type SomeObject implements C {
              e(d: D): E
            }

            union SomeUnion = F | G

            interface SomeInterface {
              i(h: H): I
            }

            input SomeInput {
              j: J
            }

            directive @SomeDirective(k: K) on QUERY

            schema {
              query: L
              mutation: M
              subscription: N
            }
            """,
            [
                TartifletteError(
                    message="Unknown type < C >.",
                    locations=[
                        Location(line=5, column=40, line_end=5, column_end=41)
                    ],
                ),
                TartifletteError(
                    message="Unknown type < D >.",
                    locations=[
                        Location(line=6, column=20, line_end=6, column_end=21)
                    ],
                ),
                TartifletteError(
                    message="Unknown type < E >.",
                    locations=[
                        Location(line=6, column=24, line_end=6, column_end=25)
                    ],
                ),
                TartifletteError(
                    message="Unknown type < F >.",
                    locations=[
                        Location(line=9, column=31, line_end=9, column_end=32)
                    ],
                ),
                TartifletteError(
                    message="Unknown type < G >.",
                    locations=[
                        Location(line=9, column=35, line_end=9, column_end=36)
                    ],
                ),
                TartifletteError(
                    message="Unknown type < H >.",
                    locations=[
                        Location(
                            line=12, column=20, line_end=12, column_end=21
                        )
                    ],
                ),
                TartifletteError(
                    message="Unknown type < I >.",
                    locations=[
                        Location(
                            line=12, column=24, line_end=12, column_end=25
                        )
                    ],
                ),
                TartifletteError(
                    message="Unknown type < J >.",
                    locations=[
                        Location(
                            line=16, column=18, line_end=16, column_end=19
                        )
                    ],
                ),
                TartifletteError(
                    message="Unknown type < K >.",
                    locations=[
                        Location(
                            line=19, column=41, line_end=19, column_end=42
                        )
                    ],
                ),
                TartifletteError(
                    message="Unknown type < L >.",
                    locations=[
                        Location(
                            line=22, column=22, line_end=22, column_end=23
                        )
                    ],
                ),
                TartifletteError(
                    message="Unknown type < M >.",
                    locations=[
                        Location(
                            line=23, column=25, line_end=23, column_end=26
                        )
                    ],
                ),
                TartifletteError(
                    message="Unknown type < N >.",
                    locations=[
                        Location(
                            line=24, column=29, line_end=24, column_end=30
                        )
                    ],
                ),
            ],
        ),
        (
            None,
            """
            directive @Foo on QUERY

            type Query {
              foo: Foo
            }
            """,
            [
                TartifletteError(
                    message="Unknown type < Foo >.",
                    locations=[
                        Location(line=5, column=20, line_end=5, column_end=23)
                    ],
                )
            ],
        ),
        (
            """
            scalar String
            scalar Int
            scalar Float
            scalar Boolean
            scalar ID

            type Foo
            """,
            """
            type SomeType {
              string: String
              int: Int
              float: Float
              boolean: Boolean
              id: ID
            }
            """,
            [],
        ),
        (
            """
            type Foo
            """,
            """
            type QueryRoot {
              foo: Foo
              bar: Bar
            }

            scalar Bar

            schema {
              query: QueryRoot
            }
            """,
            [],
        ),
        (
            """
            type A
            """,
            """
            type B

            type SomeObject implements C {
              e(d: D): E
            }

            union SomeUnion = F | G

            interface SomeInterface {
              i(h: H): I
            }

            input SomeInput {
              j: J
            }

            directive @SomeDirective(k: K) on QUERY

            schema {
              query: L
              mutation: M
              subscription: N
            }
            """,
            [
                TartifletteError(
                    message="Unknown type < C >.",
                    locations=[
                        Location(line=4, column=40, line_end=4, column_end=41)
                    ],
                ),
                TartifletteError(
                    message="Unknown type < D >.",
                    locations=[
                        Location(line=5, column=20, line_end=5, column_end=21)
                    ],
                ),
                TartifletteError(
                    message="Unknown type < E >.",
                    locations=[
                        Location(line=5, column=24, line_end=5, column_end=25)
                    ],
                ),
                TartifletteError(
                    message="Unknown type < F >.",
                    locations=[
                        Location(line=8, column=31, line_end=8, column_end=32)
                    ],
                ),
                TartifletteError(
                    message="Unknown type < G >.",
                    locations=[
                        Location(line=8, column=35, line_end=8, column_end=36)
                    ],
                ),
                TartifletteError(
                    message="Unknown type < H >.",
                    locations=[
                        Location(
                            line=11, column=20, line_end=11, column_end=21
                        )
                    ],
                ),
                TartifletteError(
                    message="Unknown type < I >.",
                    locations=[
                        Location(
                            line=11, column=24, line_end=11, column_end=25
                        )
                    ],
                ),
                TartifletteError(
                    message="Unknown type < J >.",
                    locations=[
                        Location(
                            line=15, column=18, line_end=15, column_end=19
                        )
                    ],
                ),
                TartifletteError(
                    message="Unknown type < K >.",
                    locations=[
                        Location(
                            line=18, column=41, line_end=18, column_end=42
                        )
                    ],
                ),
                TartifletteError(
                    message="Unknown type < L >.",
                    locations=[
                        Location(
                            line=21, column=22, line_end=21, column_end=23
                        )
                    ],
                ),
                TartifletteError(
                    message="Unknown type < M >.",
                    locations=[
                        Location(
                            line=22, column=25, line_end=22, column_end=26
                        )
                    ],
                ),
                TartifletteError(
                    message="Unknown type < N >.",
                    locations=[
                        Location(
                            line=23, column=29, line_end=23, column_end=30
                        )
                    ],
                ),
            ],
        ),
    ],
)
async def test_known_type_names(old_sdl, new_sdl, expected):
    old_schema = None
    if old_sdl:
        old_schema = schema_from_sdl(old_sdl, "test_known_type_names")
        await old_schema.bake(run_validation=False)
    assert (
        validate_sdl(
            parse_to_document(new_sdl), old_schema, rules=[KnownTypeNamesRule]
        )
        == expected
    )
