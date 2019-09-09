from tartiflette.language.visitor.constants import SKIP
from tartiflette.types.input_object import GraphQLInputObjectType
from tartiflette.types.interface import GraphQLInterfaceType
from tartiflette.types.object import GraphQLObjectType
from tartiflette.utils.errors import graphql_error_from_nodes
from tartiflette.validation.rules.base import ASTValidationRule

__all__ = ("UniqueFieldDefinitionNamesRule",)


def _has_field(graphql_type: "GraphQLType", field_name: str) -> bool:
    """
    TODO:
    :param graphql_type: TODO:
    :param field_name: TODO:
    :type graphql_type: TODO:
    :type field_name: TODO:
    :return: TODO:
    :rtype: TODO:
    """
    return (
        graphql_type.has_field(field_name)
        if isinstance(
            graphql_type,
            (GraphQLObjectType, GraphQLInterfaceType, GraphQLInputObjectType),
        )
        else False
    )


class UniqueFieldDefinitionNamesRule(ASTValidationRule):
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
        self.existing_types = schema.type_definitions if schema else {}
        self.known_field_names = {}

    def check_field_uniqueness(self, node, *_args):
        if node.fields:
            type_name = node.name.value
            self.known_field_names.setdefault(type_name, {})

            field_names = self.known_field_names[type_name]
            for field_definition in node.fields:
                field_name = field_definition.name.value

                if _has_field(self.existing_types.get(type_name), field_name):
                    self.context.report_error(
                        graphql_error_from_nodes(
                            f"Field < {type_name}.{field_name} > already "
                            "exists in the schema. It cannot also be defined "
                            "in this type extension.",
                            nodes=[field_definition.name],
                        )
                    )
                elif field_name in field_names:
                    self.context.report_error(
                        graphql_error_from_nodes(
                            f"Field < {type_name}.{field_name} > can only be "
                            "defined once.",
                            nodes=[
                                field_names[field_name],
                                field_definition.name,
                            ],
                        )
                    )
                else:
                    field_names[field_name] = field_definition.name
        return SKIP

    enter_InputObjectTypeDefinition = check_field_uniqueness
    enter_InputObjectTypeExtension = check_field_uniqueness
    enter_InterfaceTypeDefinition = check_field_uniqueness
    enter_InterfaceTypeExtension = check_field_uniqueness
    enter_ObjectTypeDefinition = check_field_uniqueness
    enter_ObjectTypeExtension = check_field_uniqueness
