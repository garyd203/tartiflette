from tartiflette.utils.errors import graphql_error_from_nodes
from tartiflette.validation.rules.base import ASTValidationRule

__all__ = ("LoneSchemaDefinitionRule",)


class LoneSchemaDefinitionRule(ASTValidationRule):
    """
    TODO:
    """

    def __init__(self, context: "ASTValidationContext") -> None:
        """
        :param context: TODO:
        :type context: TODO:
        """
        super().__init__(context)
        old_schema = context.schema
        self.already_defined = old_schema and (
            old_schema.queryType
            or old_schema.mutationType
            or old_schema.subscriptionType
        )
        self.schema_definitions_count = 0

    def enter_SchemaDefinition(  # pylint: disable=invalid-name
        self, node: "SchemaDefinitionNode", *_args
    ):
        if self.already_defined:
            self.context.report_error(
                graphql_error_from_nodes(
                    "Cannot define a new schema within a schema extension.",
                    nodes=[node],
                )
            )
            return

        if self.schema_definitions_count > 0:
            self.context.report_error(
                graphql_error_from_nodes(
                    "Must provide only one schema definition.", nodes=[node]
                )
            )
        self.schema_definitions_count += 1
