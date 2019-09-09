from typing import Dict, Optional, Union

from tartiflette.language.visitor.constants import SKIP
from tartiflette.utils.errors import graphql_error_from_nodes
from tartiflette.validation.rules.base import ASTValidationRule

__all__ = ("UniqueOperationTypesRule",)


class UniqueOperationTypesRule(ASTValidationRule):
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
        self.defined_operation_types: Dict[
            str, "OperationTypeDefinitionNode"
        ] = {}
        self.existing_operation_types: Dict[
            str, "OperationTypeDefinitionNode"
        ] = (
            {
                "query": schema.queryType,
                "mutation": schema.mutationType,
                "subscription": schema.subscriptionType,
            }
            if schema
            else {}
        )

    def check_operation_types(
        self,
        node: Union["SchemaDefinitionNode", "SchemaExtensionNode"],
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
        if node.operation_type_definitions:
            for operation_type_definition in node.operation_type_definitions:
                operation_type: str = operation_type_definition.operation_type
                already_defined_operation_type: Optional[
                    "OperationTypeDefinitionNode"
                ] = self.defined_operation_types.get(operation_type)

                if self.existing_operation_types.get(operation_type):
                    self.context.report_error(
                        graphql_error_from_nodes(
                            f"Type for < {operation_type} > already defined in the schema. It cannot be redefined.",
                            nodes=[operation_type_definition],
                        )
                    )
                elif already_defined_operation_type:
                    self.context.report_error(
                        graphql_error_from_nodes(
                            f"There can be only one < {operation_type} > type in schema.",
                            nodes=[
                                already_defined_operation_type,
                                operation_type_definition,
                            ],
                        )
                    )
                else:
                    self.defined_operation_types[
                        operation_type
                    ] = operation_type_definition

        return SKIP

    enter_SchemaDefinition = check_operation_types
    enter_SchemaExtension = check_operation_types
