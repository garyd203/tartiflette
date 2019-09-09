from .known_argument_names import KnownArgumentNamesOnDirectivesRule
from .known_directives import KnownDirectivesRule
from .known_type_names import KnownTypeNamesRule
from .lone_schema_definition import LoneSchemaDefinitionRule
from .possible_type_extensions import PossibleTypeExtensionsRule
from .provided_required_arguments import (
    ProvidedRequiredArgumentsOnDirectivesRule,
)
from .unique_argument_names import UniqueArgumentNamesRule
from .unique_directive_names import UniqueDirectiveNamesRule
from .unique_directives_per_location import UniqueDirectivesPerLocationRule
from .unique_enum_value_names import UniqueEnumValueNamesRule
from .unique_field_definition_names import UniqueFieldDefinitionNamesRule
from .unique_input_field_names import UniqueInputFieldNamesRule
from .unique_operation_types import UniqueOperationTypesRule
from .unique_type_names import UniqueTypeNamesRule

SPECIFIED_SDL_RULES = [
    LoneSchemaDefinitionRule,
    UniqueOperationTypesRule,
    UniqueTypeNamesRule,
    UniqueEnumValueNamesRule,
    UniqueFieldDefinitionNamesRule,
    UniqueDirectiveNamesRule,
    KnownTypeNamesRule,
    KnownDirectivesRule,
    UniqueDirectivesPerLocationRule,
    PossibleTypeExtensionsRule,
    KnownArgumentNamesOnDirectivesRule,
    UniqueArgumentNamesRule,
    UniqueInputFieldNamesRule,
    ProvidedRequiredArgumentsOnDirectivesRule,
]

__all__ = ("SPECIFIED_SDL_RULES",)
