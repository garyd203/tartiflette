from typing import Dict

from tartiflette.utils.errors import graphql_error_from_nodes
from tartiflette.validation.rules.base import ASTValidationRule

__all__ = ("UniqueDirectivesPerLocationRule",)


class UniqueDirectivesPerLocationRule(ASTValidationRule):
    """
    TODO:
    """

    def enter(self, node: "Node", *_):
        # Many different AST nodes may contain directives. Rather than listing
        # them all, just listen for entering any node, and check to see if it
        # defines any directives.
        directives = getattr(node, "directives", None)
        if directives:
            known_directives: Dict[str, "DirectiveNode"] = {}
            for directive in directives:
                directive_name = directive.name.value
                known_directive = known_directives.get(directive_name)
                if known_directive:
                    self.context.report_error(
                        graphql_error_from_nodes(
                            f"The directive < {directive_name} > can only be "
                            "used once at this location.",
                            nodes=[known_directive, directive],
                        )
                    )
                else:
                    known_directives[directive_name] = directive
