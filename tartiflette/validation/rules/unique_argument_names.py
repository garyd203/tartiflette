from typing import Dict

from tartiflette.language.visitor.constants import SKIP
from tartiflette.utils.errors import graphql_error_from_nodes
from tartiflette.validation.rules.base import ASTValidationRule

__all__ = ("UniqueArgumentNamesRule",)


class UniqueArgumentNamesRule(ASTValidationRule):
    """
    TODO:
    """

    def __init__(self, context: "ASTValidationContext") -> None:
        """
        :param context: TODO:
        :type context: TODO:
        """
        super().__init__(context)
        self.known_arguments: Dict[str, "NameNode"] = {}

    def enter_Field(self, *_args):  # pylint: disable=invalid-name
        self.known_arguments: Dict[str, "NameNode"] = {}

    def enter_Directive(self, *_args):  # pylint: disable=invalid-name
        self.known_arguments: Dict[str, "NameNode"] = {}

    def enter_Argument(  # pylint: disable=invalid-name
        self, node: "ArgumentNode", *_args
    ):
        argument_name = node.name.value
        known_argument = self.known_arguments.get(argument_name)
        if known_argument:
            self.context.report_error(
                graphql_error_from_nodes(
                    f"There can be only one argument named < {argument_name} >.",
                    nodes=[known_argument, node.name],
                )
            )
        else:
            self.known_arguments[argument_name] = node.name
        return SKIP
