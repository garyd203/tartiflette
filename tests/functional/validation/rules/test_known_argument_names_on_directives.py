import pytest

from tartiflette import TartifletteError
from tartiflette.language.ast import Location
from tartiflette.language.parsers.lark import parse_to_document
from tartiflette.schema.transformer import schema_from_sdl
from tartiflette.validation.rules import KnownArgumentNamesOnDirectivesRule
from tartiflette.validation.validate import validate_sdl

_SKIP_DIRECTIVE = """
directive @skip(if: Boolean!) on FIELD_DEFINITION
"""
_TEST_DIRECTIVE = """
directive @test(arg: String) on FIELD_DEFINITION
"""


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "old_sdl,new_sdl,expected",
    [
        (
            None,
            f"""
            {_SKIP_DIRECTIVE}
            type Query {{
              dog: String @skip(if: true)
            }}
            """,
            [],
        ),
        (
            None,
            f"""
            {_SKIP_DIRECTIVE}
            type Query {{
              dog: String @skip(unless: true)
            }}
            """,
            [
                TartifletteError(
                    message="Unknown argument < unless > on directive < @skip >.",
                    locations=[
                        Location(line=6, column=33, line_end=6, column_end=45)
                    ],
                )
            ],
        ),
        (
            None,
            f"""
            {_SKIP_DIRECTIVE}
            type Query {{
              dog: String @skip(iff: true)
            }}
            """,
            [
                TartifletteError(
                    message="Unknown argument < iff > on directive < @skip >.Did you mean if?",
                    locations=[
                        Location(line=6, column=33, line_end=6, column_end=42)
                    ],
                )
            ],
        ),
        (
            None,
            """
            type Query {
              foo: String @test(arg: "")
            }
            """
            + _TEST_DIRECTIVE,
            [],
        ),
        (
            None,
            """
            type Query {
              foo: String @test(unknown: "")
            }
            """
            + _TEST_DIRECTIVE,
            [
                TartifletteError(
                    message="Unknown argument < unknown > on directive < @test >.",
                    locations=[
                        Location(line=3, column=33, line_end=3, column_end=44)
                    ],
                )
            ],
        ),
        (
            None,
            """
            type Query {
              foo: String @test(agr: "")
            }
            """
            + _TEST_DIRECTIVE,
            [
                TartifletteError(
                    message="Unknown argument < agr > on directive < @test >.Did you mean arg?",
                    locations=[
                        Location(line=3, column=33, line_end=3, column_end=40)
                    ],
                )
            ],
        ),
        (
            None,
            """
            type Query {
              foo: String @deprecated(unknown: "")
            }
            directive @deprecated(reason: String) on FIELD_DEFINITION
            """,
            [
                TartifletteError(
                    message="Unknown argument < unknown > on directive < @deprecated >.",
                    locations=[
                        Location(line=3, column=39, line_end=3, column_end=50)
                    ],
                )
            ],
        ),
        (
            None,
            """
            type Query {
              foo: String @deprecated(reason: "")
            }
            directive @deprecated(arg: String) on FIELD
            """,
            [
                TartifletteError(
                    message="Unknown argument < reason > on directive < @deprecated >.",
                    locations=[
                        Location(line=3, column=39, line_end=3, column_end=49)
                    ],
                )
            ],
        ),
        (
            """
            type Query {
              foo: String
            }
            """,
            """
            directive @test(arg: String) on OBJECT

            extend type Query  @test(unknown: "")
            """,
            [
                TartifletteError(
                    message="Unknown argument < unknown > on directive < @test >.",
                    locations=[
                        Location(line=4, column=38, line_end=4, column_end=49)
                    ],
                )
            ],
        ),
        (
            """
            directive @test(arg: String) on OBJECT

            type Query {
              foo: String
            }
            """,
            """
            extend type Query @test(unknown: "")
            """,
            [
                TartifletteError(
                    message="Unknown argument < unknown > on directive < @test >.",
                    locations=[
                        Location(line=2, column=37, line_end=2, column_end=48)
                    ],
                )
            ],
        ),
    ],
)
async def test_known_argument_names_on_directives(old_sdl, new_sdl, expected):
    old_schema = None
    if old_sdl:
        old_schema = schema_from_sdl(
            old_sdl, "test_known_argument_names_on_directives"
        )
        await old_schema.bake(run_validation=False)
    assert (
        validate_sdl(
            parse_to_document(new_sdl),
            old_schema,
            rules=[KnownArgumentNamesOnDirectivesRule],
        )
        == expected
    )
