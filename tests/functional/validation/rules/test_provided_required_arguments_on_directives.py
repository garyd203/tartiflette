import pytest

from tartiflette import TartifletteError
from tartiflette.language.ast import Location
from tartiflette.language.parsers.lark import parse_to_document
from tartiflette.schema.transformer import schema_from_sdl
from tartiflette.validation.rules import (
    ProvidedRequiredArgumentsOnDirectivesRule,
)
from tartiflette.validation.validate import validate_sdl


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "old_sdl,new_sdl,expected",
    [
        (
            None,
            """
            type Query {
              foo: String @test
            }

            directive @test(arg1: String, arg2: String! = "") on FIELD_DEFINITION
            """,
            [],
        ),
        (
            None,
            """
            type Query {
              foo: String @test
            }

            directive @test(arg: String!) on FIELD_DEFINITION
            """,
            [
                TartifletteError(
                    message="Directive < test > argument < arg > of type < String! > required, but it was not provided.",
                    locations=[
                        Location(line=3, column=27, line_end=3, column_end=32)
                    ],
                )
            ],
        ),
        (
            None,
            """
            type Query {
              foo: String @include
            }
            directive @include(if: Boolean!) on FIELD | FRAGMENT_SPREAD | INLINE_FRAGMENT
            """,
            [
                TartifletteError(
                    message="Directive < include > argument < if > of type < Boolean! > required, but it was not provided.",
                    locations=[
                        Location(line=3, column=27, line_end=3, column_end=35)
                    ],
                )
            ],
        ),
        (
            None,
            """
            type Query {
              foo: String @deprecated
            }
            directive @deprecated(reason: String!) on FIELD
            """,
            [
                TartifletteError(
                    message="Directive < deprecated > argument < reason > of type < String! > required, but it was not provided.",
                    locations=[
                        Location(line=3, column=27, line_end=3, column_end=38)
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
            directive @test(arg: String!) on OBJECT

            extend type Query @test
            """,
            [
                TartifletteError(
                    message="Directive < test > argument < arg > of type < String! > required, but it was not provided.",
                    locations=[
                        Location(line=4, column=31, line_end=4, column_end=36)
                    ],
                )
            ],
        ),
        (
            """
            scalar String

            type Query {
              foo: String
            }

            directive @test(arg1: String, arg2: String! = "") on FIELD_DEFINITION
            """,
            """
            extend type Query @test
            """,
            [],
        ),
        (
            """
            scalar String

            type Query {
              foo: String
            }

            directive @test(arg: String!) on FIELD_DEFINITION
            """,
            """
            extend type Query @test
            """,
            [
                TartifletteError(
                    message="Directive < test > argument < arg > of type < String! > required, but it was not provided.",
                    locations=[
                        Location(line=2, column=31, line_end=2, column_end=36)
                    ],
                )
            ],
        ),
        (
            """
            scalar String

            input MyInput {
              field: String
            }

            type Query {
              foo: String
            }

            directive @test(arg: [MyInput]!) on FIELD_DEFINITION
            """,
            """
            extend type Query @test
            """,
            [
                TartifletteError(
                    message="Directive < test > argument < arg > of type < [MyInput]! > required, but it was not provided.",
                    locations=[
                        Location(line=2, column=31, line_end=2, column_end=36)
                    ],
                )
            ],
        ),
    ],
)
async def test_provided_required_arguments_on_directives(
    old_sdl, new_sdl, expected
):
    old_schema = None
    if old_sdl:
        old_schema = schema_from_sdl(
            old_sdl, "test_provided_required_arguments_on_directives"
        )
        await old_schema.bake(run_validation=False)
    assert (
        validate_sdl(
            parse_to_document(new_sdl),
            old_schema,
            rules=[ProvidedRequiredArgumentsOnDirectivesRule],
        )
        == expected
    )
