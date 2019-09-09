from difflib import get_close_matches
from typing import Dict, List

from tartiflette.language.ast import DirectiveDefinitionNode
from tartiflette.language.visitor.constants import SKIP
from tartiflette.utils.errors import did_you_mean, graphql_error_from_nodes
from tartiflette.validation.rules.base import ASTValidationRule

__all__ = ("KnownArgumentNamesOnDirectivesRule",)


class KnownArgumentNamesOnDirectivesRule(ASTValidationRule):
    """
    TODO:
    """

    def __init__(self, context: "ASTValidationContext") -> None:
        """
        :param context: TODO:
        :type context: TODO:
        """
        super().__init__(context)
        self.directive_arguments: Dict[str, List[str]] = (
            {
                directive.name: list(directive.arguments.keys())
                for directive in context.schema.directive_definitions.values()
            }
            if context.schema
            else {}
        )
        self.directive_arguments.update(
            {
                directive_definition.name.value: (
                    [
                        argument.name.value
                        for argument in directive_definition.arguments
                    ]
                    if directive_definition.arguments
                    else []
                )
                for directive_definition in context.document_node.definitions
                if isinstance(directive_definition, DirectiveDefinitionNode)
            }
        )

    def enter_Directive(  # pylint: disable=invalid-name
        self, node: "DirectiveNode", *_
    ):
        directive_name = node.name.value
        known_args = self.directive_arguments.get(directive_name)

        if known_args and node.arguments:
            for argument_node in node.arguments:
                argument_name = argument_node.name.value
                if argument_name not in known_args:
                    suggestions = get_close_matches(
                        argument_name, known_args, n=5
                    )
                    self.context.report_error(
                        graphql_error_from_nodes(
                            f"Unknown argument < {argument_name} > on "
                            f"directive < @{directive_name} >."
                            + did_you_mean(suggestions),
                            nodes=[argument_node],
                        )
                    )
        return SKIP
