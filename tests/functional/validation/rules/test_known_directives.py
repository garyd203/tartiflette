import pytest

from tartiflette import TartifletteError
from tartiflette.language.ast import Location
from tartiflette.language.parsers.lark import parse_to_document
from tartiflette.schema.transformer import schema_from_sdl
from tartiflette.validation.rules import KnownDirectivesRule
from tartiflette.validation.validate import validate_sdl

_SCHEMA_WITH_SDL_DIRECTIVES = """
directive @onSchema on SCHEMA
directive @onScalar on SCALAR
directive @onObject on OBJECT
directive @onFieldDefinition on FIELD_DEFINITION
directive @onArgumentDefinition on ARGUMENT_DEFINITION
directive @onInterface on INTERFACE
directive @onUnion on UNION
directive @onEnum on ENUM
directive @onEnumValue on ENUM_VALUE
directive @onInputObject on INPUT_OBJECT
directive @onInputFieldDefinition on INPUT_FIELD_DEFINITION
"""


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

            directive @test on FIELD_DEFINITION
            """,
            [],
        ),
        (
            None,
            """
            directive @deprecated on FIELD_DEFINITION

            type Query {
              foo: String @deprecated
            }
            """,
            [],
        ),
        (
            None,
            """
            schema @deprecated {
              query: Query
            }
            directive @deprecated on SCHEMA
            """,
            [],
        ),
        (
            """
            type Query {
              foo: String
            }
            """,
            """
            directive @test on OBJECT

            extend type Query @test
            """,
            [],
        ),
        (
            """
            directive @test on OBJECT

            type Query {
              foo: String
            }
            """,
            """
            extend type Query @test
            """,
            [],
        ),
        (
            """
            type Query {
              foo: String
            }
            """,
            """
            extend type Query @unknown
            """,
            [
                TartifletteError(
                    message="Unknown directive < unknown >.",
                    locations=[
                        Location(line=2, column=31, line_end=2, column_end=39)
                    ],
                )
            ],
        ),
        (
            _SCHEMA_WITH_SDL_DIRECTIVES,
            """
            type MyObj implements MyInterface @onObject {
              myField(myArg: Int @onArgumentDefinition): String @onFieldDefinition
            }

            extend type MyObj @onObject

            scalar MyScalar @onScalar

            extend scalar MyScalar @onScalar

            interface MyInterface @onInterface {
              myField(myArg: Int @onArgumentDefinition): String @onFieldDefinition
            }

            extend interface MyInterface @onInterface

            union MyUnion @onUnion = MyObj | Other

            extend union MyUnion @onUnion

            enum MyEnum @onEnum {
              MY_VALUE @onEnumValue
            }

            extend enum MyEnum @onEnum

            input MyInput @onInputObject {
              myField: Int @onInputFieldDefinition
            }

            extend input MyInput @onInputObject

            schema @onSchema {
              query: MyQuery
            }

            extend schema @onSchema
            """,
            [],
        ),
        (
            _SCHEMA_WITH_SDL_DIRECTIVES,
            """
            type MyObj implements MyInterface @onInterface {
              myField(myArg: Int @onInputFieldDefinition): String @onInputFieldDefinition
            }

            scalar MyScalar @onEnum

            interface MyInterface @onObject {
              myField(myArg: Int @onInputFieldDefinition): String @onInputFieldDefinition
            }

            union MyUnion @onEnumValue = MyObj | Other

            enum MyEnum @onScalar {
              MY_VALUE @onUnion
            }

            input MyInput @onEnum {
              myField: Int @onArgumentDefinition
            }

            schema @onObject {
              query: MyQuery
            }

            extend schema @onObject
            """,
            [
                TartifletteError(
                    message="Directive < onInterface > may not be used on OBJECT.",
                    locations=[
                        Location(line=2, column=47, line_end=2, column_end=59)
                    ],
                ),
                TartifletteError(
                    message="Directive < onInputFieldDefinition > may not be used on ARGUMENT_DEFINITION.",
                    locations=[
                        Location(line=3, column=34, line_end=3, column_end=57)
                    ],
                ),
                TartifletteError(
                    message="Directive < onInputFieldDefinition > may not be used on FIELD_DEFINITION.",
                    locations=[
                        Location(line=3, column=67, line_end=3, column_end=90)
                    ],
                ),
                TartifletteError(
                    message="Directive < onEnum > may not be used on SCALAR.",
                    locations=[
                        Location(line=6, column=29, line_end=6, column_end=36)
                    ],
                ),
                TartifletteError(
                    message="Directive < onObject > may not be used on INTERFACE.",
                    locations=[
                        Location(line=8, column=35, line_end=8, column_end=44)
                    ],
                ),
                TartifletteError(
                    message="Directive < onInputFieldDefinition > may not be used on ARGUMENT_DEFINITION.",
                    locations=[
                        Location(line=9, column=34, line_end=9, column_end=57)
                    ],
                ),
                TartifletteError(
                    message="Directive < onInputFieldDefinition > may not be used on FIELD_DEFINITION.",
                    locations=[
                        Location(line=9, column=67, line_end=9, column_end=90)
                    ],
                ),
                TartifletteError(
                    message="Directive < onEnumValue > may not be used on UNION.",
                    locations=[
                        Location(
                            line=12, column=27, line_end=12, column_end=39
                        )
                    ],
                ),
                TartifletteError(
                    message="Directive < onScalar > may not be used on ENUM.",
                    locations=[
                        Location(
                            line=14, column=25, line_end=14, column_end=34
                        )
                    ],
                ),
                TartifletteError(
                    message="Directive < onUnion > may not be used on ENUM_VALUE.",
                    locations=[
                        Location(
                            line=15, column=24, line_end=15, column_end=32
                        )
                    ],
                ),
                TartifletteError(
                    message="Directive < onEnum > may not be used on INPUT_OBJECT.",
                    locations=[
                        Location(
                            line=18, column=27, line_end=18, column_end=34
                        )
                    ],
                ),
                TartifletteError(
                    message="Directive < onArgumentDefinition > may not be used on INPUT_FIELD_DEFINITION.",
                    locations=[
                        Location(
                            line=19, column=28, line_end=19, column_end=49
                        )
                    ],
                ),
                TartifletteError(
                    message="Directive < onObject > may not be used on SCHEMA.",
                    locations=[
                        Location(
                            line=22, column=20, line_end=22, column_end=29
                        )
                    ],
                ),
                TartifletteError(
                    message="Directive < onObject > may not be used on SCHEMA.",
                    locations=[
                        Location(
                            line=26, column=27, line_end=26, column_end=36
                        )
                    ],
                ),
            ],
        ),
    ],
)
async def test_known_directives(old_sdl, new_sdl, expected):
    old_schema = None
    if old_sdl:
        old_schema = schema_from_sdl(old_sdl, "test_known_directives")
        await old_schema.bake(run_validation=False)
    assert (
        validate_sdl(
            parse_to_document(new_sdl), old_schema, rules=[KnownDirectivesRule]
        )
        == expected
    )
