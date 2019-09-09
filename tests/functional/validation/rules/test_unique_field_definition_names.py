import pytest

from tartiflette import TartifletteError
from tartiflette.language.ast import Location
from tartiflette.language.parsers.lark import parse_to_document
from tartiflette.schema.transformer import schema_from_sdl
from tartiflette.validation.rules import UniqueFieldDefinitionNamesRule
from tartiflette.validation.validate import validate_sdl


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "old_sdl,new_sdl,expected",
    [
        (
            None,
            """
            type SomeObject
            interface SomeInterface
            input SomeInputObject
            """,
            [],
        ),
        (
            None,
            """
            type SomeObject {
              foo: String
            }

            interface SomeInterface {
              foo: String
            }

            input SomeInputObject {
              foo: String
            }
            """,
            [],
        ),
        (
            None,
            """
            type SomeObject {
              foo: String
              bar: String
            }

            interface SomeInterface {
              foo: String
              bar: String
            }

            input SomeInputObject {
              foo: String
              bar: String
            }
            """,
            [],
        ),
        (
            None,
            """
            type SomeObject {
              foo: String
              bar: String
              foo: String
            }

            interface SomeInterface {
              foo: String
              bar: String
              foo: String
            }

            input SomeInputObject {
              foo: String
              bar: String
              foo: String
            }
            """,
            [
                TartifletteError(
                    message="Field < SomeObject.foo > can only be defined once.",
                    locations=[
                        Location(line=3, column=15, line_end=3, column_end=18),
                        Location(line=5, column=15, line_end=5, column_end=18),
                    ],
                ),
                TartifletteError(
                    message="Field < SomeInterface.foo > can only be defined once.",
                    locations=[
                        Location(line=9, column=15, line_end=9, column_end=18),
                        Location(
                            line=11, column=15, line_end=11, column_end=18
                        ),
                    ],
                ),
                TartifletteError(
                    message="Field < SomeInputObject.foo > can only be defined once.",
                    locations=[
                        Location(
                            line=15, column=15, line_end=15, column_end=18
                        ),
                        Location(
                            line=17, column=15, line_end=17, column_end=18
                        ),
                    ],
                ),
            ],
        ),
        (
            None,
            """
            type SomeObject {
              foo: String
            }
            extend type SomeObject {
              bar: String
            }
            extend type SomeObject {
              baz: String
            }

            interface SomeInterface {
              foo: String
            }
            extend interface SomeInterface {
              bar: String
            }
            extend interface SomeInterface {
              baz: String
            }

            input SomeInputObject {
              foo: String
            }
            extend input SomeInputObject {
              bar: String
            }
            extend input SomeInputObject {
              baz: String
            }
            """,
            [],
        ),
        (
            None,
            """
            extend type SomeObject {
              foo: String
            }
            type SomeObject {
              foo: String
            }

            extend interface SomeInterface {
              foo: String
            }
            interface SomeInterface {
              foo: String
            }

            extend input SomeInputObject {
              foo: String
            }
            input SomeInputObject {
              foo: String
            }
            """,
            [
                TartifletteError(
                    message="Field < SomeObject.foo > can only be defined once.",
                    locations=[
                        Location(line=3, column=15, line_end=3, column_end=18),
                        Location(line=6, column=15, line_end=6, column_end=18),
                    ],
                ),
                TartifletteError(
                    message="Field < SomeInterface.foo > can only be defined once.",
                    locations=[
                        Location(
                            line=10, column=15, line_end=10, column_end=18
                        ),
                        Location(
                            line=13, column=15, line_end=13, column_end=18
                        ),
                    ],
                ),
                TartifletteError(
                    message="Field < SomeInputObject.foo > can only be defined once.",
                    locations=[
                        Location(
                            line=17, column=15, line_end=17, column_end=18
                        ),
                        Location(
                            line=20, column=15, line_end=20, column_end=18
                        ),
                    ],
                ),
            ],
        ),
        (
            None,
            """
            type SomeObject
            extend type SomeObject {
              foo: String
              bar: String
              foo: String
            }

            interface SomeInterface
            extend interface SomeInterface {
              foo: String
              bar: String
              foo: String
            }

            input SomeInputObject
            extend input SomeInputObject {
              foo: String
              bar: String
              foo: String
            }
            """,
            [
                TartifletteError(
                    message="Field < SomeObject.foo > can only be defined once.",
                    locations=[
                        Location(line=4, column=15, line_end=4, column_end=18),
                        Location(line=6, column=15, line_end=6, column_end=18),
                    ],
                ),
                TartifletteError(
                    message="Field < SomeInterface.foo > can only be defined once.",
                    locations=[
                        Location(
                            line=11, column=15, line_end=11, column_end=18
                        ),
                        Location(
                            line=13, column=15, line_end=13, column_end=18
                        ),
                    ],
                ),
                TartifletteError(
                    message="Field < SomeInputObject.foo > can only be defined once.",
                    locations=[
                        Location(
                            line=18, column=15, line_end=18, column_end=18
                        ),
                        Location(
                            line=20, column=15, line_end=20, column_end=18
                        ),
                    ],
                ),
            ],
        ),
        (
            None,
            """
            type SomeObject
            extend type SomeObject {
              foo: String
            }
            extend type SomeObject {
              foo: String
            }

            interface SomeInterface
            extend interface SomeInterface {
              foo: String
            }
            extend interface SomeInterface {
              foo: String
            }

            input SomeInputObject
            extend input SomeInputObject {
              foo: String
            }
            extend input SomeInputObject {
              foo: String
            }
            """,
            [
                TartifletteError(
                    message="Field < SomeObject.foo > can only be defined once.",
                    locations=[
                        Location(line=4, column=15, line_end=4, column_end=18),
                        Location(line=7, column=15, line_end=7, column_end=18),
                    ],
                ),
                TartifletteError(
                    message="Field < SomeInterface.foo > can only be defined once.",
                    locations=[
                        Location(
                            line=12, column=15, line_end=12, column_end=18
                        ),
                        Location(
                            line=15, column=15, line_end=15, column_end=18
                        ),
                    ],
                ),
                TartifletteError(
                    message="Field < SomeInputObject.foo > can only be defined once.",
                    locations=[
                        Location(
                            line=20, column=15, line_end=20, column_end=18
                        ),
                        Location(
                            line=23, column=15, line_end=23, column_end=18
                        ),
                    ],
                ),
            ],
        ),
        (
            """
            type SomeObject
            interface SomeInterface
            input SomeInputObject
            """,
            """
            extend type SomeObject {
              foo: String
            }

            extend interface SomeInterface {
              foo: String
            }

            extend input SomeInputObject {
              foo: String
            }
            """,
            [],
        ),
        (
            """
            type SomeObject {
              foo: String
            }

            interface SomeInterface {
              foo: String
            }

            input SomeInputObject {
              foo: String
            }
            """,
            """
            extend type SomeObject {
              foo: String
            }
            extend interface SomeInterface {
              foo: String
            }
            extend input SomeInputObject {
              foo: String
            }

            extend type SomeObject {
              foo: String
            }
            extend interface SomeInterface {
              foo: String
            }
            extend input SomeInputObject {
              foo: String
            }
            """,
            [
                TartifletteError(
                    message="Field < SomeObject.foo > already exists in the schema. It cannot also be defined in this type extension.",
                    locations=[
                        Location(line=3, column=15, line_end=3, column_end=18)
                    ],
                ),
                TartifletteError(
                    message="Field < SomeInterface.foo > already exists in the schema. It cannot also be defined in this type extension.",
                    locations=[
                        Location(line=6, column=15, line_end=6, column_end=18)
                    ],
                ),
                TartifletteError(
                    message="Field < SomeInputObject.foo > already exists in the schema. It cannot also be defined in this type extension.",
                    locations=[
                        Location(line=9, column=15, line_end=9, column_end=18)
                    ],
                ),
                TartifletteError(
                    message="Field < SomeObject.foo > already exists in the schema. It cannot also be defined in this type extension.",
                    locations=[
                        Location(
                            line=13, column=15, line_end=13, column_end=18
                        )
                    ],
                ),
                TartifletteError(
                    message="Field < SomeInterface.foo > already exists in the schema. It cannot also be defined in this type extension.",
                    locations=[
                        Location(
                            line=16, column=15, line_end=16, column_end=18
                        )
                    ],
                ),
                TartifletteError(
                    message="Field < SomeInputObject.foo > already exists in the schema. It cannot also be defined in this type extension.",
                    locations=[
                        Location(
                            line=19, column=15, line_end=19, column_end=18
                        )
                    ],
                ),
            ],
        ),
        (
            """
            type SomeObject
            interface SomeInterface
            input SomeInputObject
            """,
            """
            extend type SomeObject {
              foo: String
            }
            extend type SomeObject {
              foo: String
            }

            extend interface SomeInterface {
              foo: String
            }
            extend interface SomeInterface {
              foo: String
            }

            extend input SomeInputObject {
              foo: String
            }
            extend input SomeInputObject {
              foo: String
            }
            """,
            [
                TartifletteError(
                    message="Field < SomeObject.foo > can only be defined once.",
                    locations=[
                        Location(line=3, column=15, line_end=3, column_end=18),
                        Location(line=6, column=15, line_end=6, column_end=18),
                    ],
                ),
                TartifletteError(
                    message="Field < SomeInterface.foo > can only be defined once.",
                    locations=[
                        Location(
                            line=10, column=15, line_end=10, column_end=18
                        ),
                        Location(
                            line=13, column=15, line_end=13, column_end=18
                        ),
                    ],
                ),
                TartifletteError(
                    message="Field < SomeInputObject.foo > can only be defined once.",
                    locations=[
                        Location(
                            line=17, column=15, line_end=17, column_end=18
                        ),
                        Location(
                            line=20, column=15, line_end=20, column_end=18
                        ),
                    ],
                ),
            ],
        ),
    ],
)
async def test_unique_field_definition_names(old_sdl, new_sdl, expected):
    old_schema = None
    if old_sdl:
        old_schema = schema_from_sdl(
            old_sdl, "test_unique_field_definition_names"
        )
        await old_schema.bake(run_validation=False)
    assert (
        validate_sdl(
            parse_to_document(new_sdl),
            old_schema,
            rules=[UniqueFieldDefinitionNamesRule],
        )
        == expected
    )
