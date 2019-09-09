from typing import Dict, List

from tartiflette.utils.errors import graphql_error_from_nodes
from tartiflette.validation.rules.base import ASTValidationRule

__all__ = ("UniqueInputFieldNamesRule",)


class UniqueInputFieldNamesRule(ASTValidationRule):
    """
    TODO:
    """

    def __init__(self, context: "ASTValidationContext") -> None:
        """
        :param context: TODO:
        :type context: TODO:
        """
        super().__init__(context)
        self.known_name_stack: List[Dict[str, "NameNode"]] = []
        self.known_input_fields: Dict[str, "NameNode"] = {}

    def enter_ObjectValue(self, *_args):  # pylint: disable=invalid-name
        self.known_name_stack.append(self.known_input_fields)
        self.known_input_fields: Dict[str, "NameNode"] = {}

    def leave_ObjectValue(self, *_args):  # pylint: disable=invalid-name
        self.known_input_fields: Dict[
            str, "NameNode"
        ] = self.known_name_stack.pop()

    def enter_ObjectField(  # pylint: disable=invalid-name
        self, node: "ObjectFieldNode", *_args
    ):
        field_name = node.name.value
        known_input_field = self.known_input_fields.get(field_name)
        if known_input_field:
            self.context.report_error(
                graphql_error_from_nodes(
                    f"There can be only one input field named < {field_name} >.",
                    nodes=[known_input_field, node.name],
                )
            )
        else:
            self.known_input_fields[field_name] = node.name
