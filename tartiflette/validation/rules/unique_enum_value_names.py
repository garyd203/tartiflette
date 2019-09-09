from typing import Any, Dict, Union

from tartiflette.language.visitor.constants import SKIP
from tartiflette.types.enum import GraphQLEnumType
from tartiflette.utils.errors import graphql_error_from_nodes
from tartiflette.validation.rules.base import ASTValidationRule

__all__ = ("UniqueEnumValueNamesRule",)


class UniqueEnumValueNamesRule(ASTValidationRule):
    """
    TODO:
    """

    def __init__(self, context: "ASTValidationContext") -> None:
        """
        :param context: TODO:
        :type context: TODO:
        """
        super().__init__(context)
        schema = context.schema
        self.existing_types_map: Dict[str, Any] = (
            schema.type_definitions if schema else {}
        )
        self.known_value_names: Dict[str, Any] = {}

    def check_value_uniqueness(
        self,
        node: Union["EnumTypeDefinitionNode", "EnumTypeExtensionNode"],
        *_args,
    ):
        """
        TODO:
        :param node: TODO:
        :type node: TODO:
        :return: TODO:
        :rtype: TODO:
        """
        # pylint: disable=missing-param-doc
        type_name = node.name.value
        self.known_value_names.setdefault(type_name, {})
        if node.values:
            value_names = self.known_value_names[type_name]
            for value_def in node.values:
                value_name = value_def.name.value
                existing_type = self.existing_types_map.get(type_name)
                if isinstance(
                    existing_type, GraphQLEnumType
                ) and existing_type.has_value(value_name):
                    self.context.report_error(
                        graphql_error_from_nodes(
                            f"Enum value < {type_name}.{value_name} > already exists in the schema. It cannot also be defined in this type extension.",
                            nodes=[value_def.name],
                        )
                    )
                elif value_name in value_names:
                    self.context.report_error(
                        graphql_error_from_nodes(
                            f"Enum value < {type_name}.{value_name} > can only be defined once.",
                            nodes=[value_names[value_name], value_def.name],
                        )
                    )
                else:
                    value_names[value_name] = value_def.name
        return SKIP

    enter_EnumTypeDefinition = check_value_uniqueness
    enter_EnumTypeExtension = check_value_uniqueness
