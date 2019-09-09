import pytest

from tartiflette import TartifletteError
from tartiflette.language.ast import Location
from tartiflette.language.parsers.lark import parse_to_document
from tartiflette.validation.rules import UniqueArgumentNamesRule
from tartiflette.validation.validate import validate_sdl


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "new_sdl,expected",
    [
        # Reason: lark parser doesn't implements the query language grammar
        # (
        #     """
        #     {
        #       field
        #     }
        #     """,
        #     [],
        # ),
        # (
        #     """
        #     {
        #       field(arg: "value")
        #     }
        #     """,
        #     [],
        # ),
        # (
        #     """
        #     {
        #       field1(arg: "value")
        #       field2(arg: "value")
        #     }
        #     """,
        #     [],
        # ),
        # (
        #     """
        #     {
        #       field(arg1: "value", arg2: "value", arg3: "value")
        #     }
        #     """,
        #     [],
        # ),
        # (
        #     """
        #     {
        #       field(arg1: "value", arg1: "value")
        #     }
        #     """,
        #     [],
        # ),
        # (
        #     """
        #     {
        #       field(arg1: "value", arg1: "value", arg1: "value")
        #     }
        #     """,
        #     [],
        # ),
        (
            """
            type Query {
              field: String @directive
            }
            """,
            [],
        ),
        (
            """
            type Query {
              field: String @directive(arg: "value")
            }
            """,
            [],
        ),
        (
            """
            type Query {
              field(arg: String = "value"): String @directive(arg: "value")
            }
            """,
            [],
        ),
        (
            """
            type Query {
              field: String @directive1(arg: "value") @directive2(arg: "value")
            }
            """,
            [],
        ),
        (
            """
            type Query {
              field: String @directive(arg1: "value", arg2: "value", arg3: "value")
            }
            """,
            [],
        ),
        (
            """
            type Query {
              field: String @directive(arg1: "value", arg1: "value")
            }
            """,
            [
                TartifletteError(
                    message="There can be only one argument named < arg1 >.",
                    locations=[
                        Location(line=3, column=40, line_end=3, column_end=44),
                        Location(line=3, column=55, line_end=3, column_end=59),
                    ],
                )
            ],
        ),
        (
            """
            type Query {
              field: String @directive(arg1: "value", arg1: "value", arg1: "value")
            }
            """,
            [
                TartifletteError(
                    message="There can be only one argument named < arg1 >.",
                    locations=[
                        Location(line=3, column=40, line_end=3, column_end=44),
                        Location(line=3, column=55, line_end=3, column_end=59),
                    ],
                ),
                TartifletteError(
                    message="There can be only one argument named < arg1 >.",
                    locations=[
                        Location(line=3, column=40, line_end=3, column_end=44),
                        Location(line=3, column=70, line_end=3, column_end=74),
                    ],
                ),
            ],
        ),
    ],
)
async def test_unique_argument_names(new_sdl, expected):
    assert (
        validate_sdl(
            parse_to_document(new_sdl), rules=[UniqueArgumentNamesRule]
        )
        == expected
    )
