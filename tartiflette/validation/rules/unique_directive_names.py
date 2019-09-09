from typing import Dict

from tartiflette.language.visitor.constants import OK, SKIP
from tartiflette.utils.errors import graphql_error_from_nodes
from tartiflette.validation.rules.base import ASTValidationRule

__all__ = ("UniqueDirectiveNamesRule",)


class UniqueDirectiveNamesRule(ASTValidationRule):
    """
    TODO:
    """

    def __init__(self, context: "ASTValidationContext") -> None:
        """
        :param context: TODO:
        :type context: TODO:
        """
        super().__init__(context)
        self.known_directives: Dict[str, "NameNode"] = {}
        self.schema: "GraphQLSchema" = context.schema

    def enter_DirectiveDefinition(  # pylint: disable=invalid-name
        self, node: "DirectiveDefinitionNode", *_args
    ):
        directive_name = node.name.value

        if self.schema and self.schema.has_directive(directive_name):
            self.context.report_error(
                graphql_error_from_nodes(
                    f"Directive < {directive_name} > already exists in the schema. It cannot be redefined.",
                    nodes=[node.name],
                )
            )
            return OK

        known_directive = self.known_directives.get(directive_name)
        if known_directive:
            self.context.report_error(
                graphql_error_from_nodes(
                    f"There can be only one directive named < {directive_name} >.",
                    nodes=[known_directive, node.name],
                )
            )
        else:
            self.known_directives[directive_name] = node.name
        return SKIP
