from difflib import get_close_matches
from typing import Dict

from tartiflette.language.ast import (
    EnumTypeDefinitionNode,
    EnumTypeExtensionNode,
    InputObjectTypeDefinitionNode,
    InputObjectTypeExtensionNode,
    InterfaceTypeDefinitionNode,
    InterfaceTypeExtensionNode,
    ObjectTypeDefinitionNode,
    ObjectTypeExtensionNode,
    ScalarTypeDefinitionNode,
    ScalarTypeExtensionNode,
    UnionTypeDefinitionNode,
    UnionTypeExtensionNode,
)
from tartiflette.language.ast.base import TypeDefinitionNode
from tartiflette.types.enum import GraphQLEnumType
from tartiflette.types.input_object import GraphQLInputObjectType
from tartiflette.types.interface import GraphQLInterfaceType
from tartiflette.types.object import GraphQLObjectType
from tartiflette.types.scalar import GraphQLScalarType
from tartiflette.types.union import GraphQLUnionType
from tartiflette.utils.errors import did_you_mean, graphql_error_from_nodes
from tartiflette.validation.rules.base import ASTValidationRule

__all__ = ("PossibleTypeExtensionsRule",)


_EXTENSION_TO_TYPE_NAME = {
    ScalarTypeExtensionNode: "scalar",
    ObjectTypeExtensionNode: "object",
    InterfaceTypeExtensionNode: "interface",
    UnionTypeExtensionNode: "union",
    EnumTypeExtensionNode: "enum",
    InputObjectTypeExtensionNode: "input object",
}

_DEFINITION_TO_EXTENSION_CLASS = {
    ScalarTypeDefinitionNode: ScalarTypeExtensionNode,
    ObjectTypeDefinitionNode: ObjectTypeExtensionNode,
    InterfaceTypeDefinitionNode: InterfaceTypeExtensionNode,
    UnionTypeDefinitionNode: UnionTypeExtensionNode,
    EnumTypeDefinitionNode: EnumTypeExtensionNode,
    InputObjectTypeDefinitionNode: InputObjectTypeExtensionNode,
}

_GRAPHQL_TYPE_TO_EXTENSION_CLASS = {
    GraphQLScalarType: ScalarTypeExtensionNode,
    GraphQLObjectType: ObjectTypeExtensionNode,
    GraphQLInterfaceType: InterfaceTypeExtensionNode,
    GraphQLUnionType: UnionTypeExtensionNode,
    GraphQLEnumType: EnumTypeExtensionNode,
    GraphQLInputObjectType: InputObjectTypeExtensionNode,
}


class PossibleTypeExtensionsRule(ASTValidationRule):
    """
    TODO:
    """

    def __init__(self, context: "ASTValidationContext") -> None:
        """
        :param context: TODO:
        :type context: TODO:
        """
        super().__init__(context)
        self.schema = context.schema
        self.defined_types: Dict[str, "TypeDefinitionNode"] = {
            definition_node.name.value: definition_node
            for definition_node in context.document_node.definitions
            if isinstance(definition_node, TypeDefinitionNode)
        }

    def check_extension(self, node, *_args):
        # pylint: disable=too-many-locals
        type_name = node.name.value
        definition_node = self.defined_types.get(type_name)
        existing_type = (
            self.schema.find_type(type_name)
            if self.schema and self.schema.has_type(type_name)
            else None
        )

        if definition_node:
            expected_kind = _DEFINITION_TO_EXTENSION_CLASS.get(
                type(definition_node)
            )
            if expected_kind is None or not isinstance(node, expected_kind):
                kind = _EXTENSION_TO_TYPE_NAME.get(
                    expected_kind, "unknown type"
                )
                self.context.report_error(
                    graphql_error_from_nodes(
                        f"Cannot extend non-{kind} type < {type_name} >.",
                        nodes=[definition_node, node],
                    )
                )
        elif existing_type:
            expected_kind = _GRAPHQL_TYPE_TO_EXTENSION_CLASS.get(
                type(existing_type)
            )
            if expected_kind is None or not isinstance(node, expected_kind):
                kind = _EXTENSION_TO_TYPE_NAME.get(
                    expected_kind, "unknown type"
                )
                self.context.report_error(
                    graphql_error_from_nodes(
                        f"Cannot extend non-{kind} type < {type_name} >.",
                        nodes=[node],
                    )
                )
        else:
            all_type_names = list(self.defined_types.keys())
            if self.schema:
                all_type_names += list(self.schema.type_definitions.keys())

            suggested_types = get_close_matches(type_name, all_type_names, n=5)
            self.context.report_error(
                graphql_error_from_nodes(
                    f"Cannot extend type < {type_name} > because it is not "
                    "defined." + did_you_mean(suggested_types),
                    nodes=[node.name],
                )
            )

    enter_ScalarTypeExtension = check_extension
    enter_ObjectTypeExtension = check_extension
    enter_InterfaceTypeExtension = check_extension
    enter_UnionTypeExtension = check_extension
    enter_EnumTypeExtension = check_extension
    enter_InputObjectTypeExtension = check_extension
