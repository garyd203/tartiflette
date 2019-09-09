from typing import Dict

from tartiflette.language.visitor.constants import OK, SKIP
from tartiflette.utils.errors import graphql_error_from_nodes
from tartiflette.validation.rules.base import ASTValidationRule

__all__ = ("UniqueTypeNamesRule",)


class UniqueTypeNamesRule(ASTValidationRule):
    """
    TODO:
    """

    def __init__(self, context: "ASTValidationContext") -> None:
        """
        :param context: TODO:
        :type context: TODO:
        """
        super().__init__(context)
        self.known_type_names: Dict[str, "NameNode"] = {}
        self.schema = context.schema

    def check_type_name(self, node: "TypeDefinitionNode", *_args):
        """
        TODO:
        :param node: TODO:
        :type node: TODO:
        :return: TODO:
        :rtype: TODO:
        """
        # pylint: disable=missing-param-doc
        type_name = node.name.value

        if self.schema and self.schema.has_type(type_name):
            self.context.report_error(
                graphql_error_from_nodes(
                    f"Type < {type_name} > already exists in the schema. It "
                    "cannot also be defined in this type definition.",
                    nodes=[node.name],
                )
            )
            return OK

        known_type_name = self.known_type_names.get(type_name)
        if known_type_name:
            self.context.report_error(
                graphql_error_from_nodes(
                    f"There can be only one type named < {type_name} >.",
                    nodes=[known_type_name, node.name],
                )
            )
        else:
            self.known_type_names[type_name] = node.name

        return SKIP

    enter_ScalarTypeDefinition = check_type_name
    enter_ObjectTypeDefinition = check_type_name
    enter_InterfaceTypeDefinition = check_type_name
    enter_UnionTypeDefinition = check_type_name
    enter_EnumTypeDefinition = check_type_name
    enter_InputObjectTypeDefinition = check_type_name
