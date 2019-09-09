from difflib import get_close_matches
from typing import Any, Dict, Set

from tartiflette.language.ast.base import (
    TypeDefinitionNode,
    TypeSystemDefinitionNode,
    TypeSystemExtensionNode,
)
from tartiflette.language.visitor.constants import OK
from tartiflette.utils.errors import did_you_mean, graphql_error_from_nodes
from tartiflette.validation.rules.base import ASTValidationRule

__all__ = ("KnownTypeNamesRule",)


SPECIFIED_SCALAR_TYPES = []


def is_sdl_node(node: "Node"):
    return (
        node
        and not isinstance(node, list)
        and isinstance(
            node, (TypeSystemDefinitionNode, TypeSystemExtensionNode)
        )
    )


class KnownTypeNamesRule(ASTValidationRule):
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
        self.defined_types: Set[str] = {
            definition_node.name.value
            for definition_node in context.document_node.definitions
            if isinstance(definition_node, TypeDefinitionNode)
        }
        self.type_names = list(self.existing_types_map.keys()) + list(
            self.defined_types
        )

    def enter_NamedType(  # pylint: disable=invalid-name,inconsistent-return-statements
        self, node: "NamedType", _, parent, __, ancestors
    ):
        type_name = node.name.value
        if (
            type_name not in self.existing_types_map
            and type_name not in self.defined_types
        ):
            try:
                definition_node = ancestors[2]
            except IndexError:
                definition_node = parent

            is_sdl = is_sdl_node(definition_node)
            if is_sdl and type_name in SPECIFIED_SCALAR_TYPES:
                return OK

            suggested_types = get_close_matches(
                type_name,
                (
                    list(SPECIFIED_SCALAR_TYPES) + self.type_names
                    if is_sdl
                    else self.type_names
                ),
                n=5,
            )
            self.context.report_error(
                graphql_error_from_nodes(
                    f"Unknown type < {type_name} >."
                    + did_you_mean(suggested_types),
                    nodes=[node],
                )
            )
