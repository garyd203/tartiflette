from typing import Dict, List, Optional, Set

from tartiflette.language.ast import (
    FieldNode,
    FragmentDefinitionNode,
    FragmentSpreadNode,
    InlineFragmentNode,
    OperationDefinitionNode,
)

NODE_WITH_SELECTION_SET = (
    OperationDefinitionNode,
    FragmentDefinitionNode,
    FieldNode,
    InlineFragmentNode,
)


class ASTValidationContext:
    """
    TODO:
    """

    def __init__(self, document_node: "DocumentNode") -> None:
        """
        :param document_node: TODO:
        :type document_node: TODO:
        """
        self.document_node = document_node
        self.errors: List["TartifletteError"] = []

    def report_error(self, error: "GraphQLError") -> None:
        """
        TODO:
        :param error: TODO:
        :type error: TODO:
        """
        self.errors.append(error)


class QueryValidationContext(ASTValidationContext):
    """
    TODO:
    """

    def __init__(self, document_node: "DocumentNode") -> None:
        """
        :param document_node: TODO:
        :type document_node: TODO:
        """
        super().__init__(document_node)
        self._fragments: Optional[Dict[str, "FragmentDefinitionNode"]] = None
        self._fragment_spreads: Dict[
            "SelectionSetNode", List["FragmentSpreadNode"]
        ] = {}
        self._recursively_referenced_fragments: Dict[
            "OperationDefinitionNode", List["FragmentDefinitionNode"]
        ] = {}

    def get_fragment(self, name: str) -> Optional["FragmentDefinitionnode"]:
        """
        TODO:
        :param name: TODO:
        :type name: TODO:
        :return: TODO:
        :rtype: TODO:
        """
        if self._fragments is None:
            self._fragments = {
                definition.name.value: definition
                for definition in self.document_node.definitions
                if isinstance(definition, FragmentDefinitionNode)
            }
        return self._fragments.get(name)

    def get_fragment_spreads(
        self, selection_set_node: "SelectionSetNode"
    ) -> List["FragmentSpreadNode"]:
        """
        TODO:
        :param selection_set_node: TODO:
        :type selection_set_node: TODO:
        :return: TODO:
        :rtype: TODO:
        """
        node_id = id(selection_set_node)
        spreads = self._fragment_spreads.get(node_id)
        if spreads is None:
            spreads: List["FragmentSpreadNode"] = []
            sets_to_visit: List["SelectionSetNode"] = [selection_set_node]
            while sets_to_visit:
                set_to_visit = sets_to_visit.pop()
                for selection in set_to_visit.selections:
                    if isinstance(selection, FragmentSpreadNode):
                        spreads.append(selection)
                    elif (
                        isinstance(selection, NODE_WITH_SELECTION_SET)
                        and selection.selection_set
                    ):
                        sets_to_visit.append(selection.selection_set)
            self._fragment_spreads[node_id] = spreads
        return spreads

    def get_recursively_referenced_fragments(
        self, operation_node: "OperationDefinitionNode"
    ) -> List["FragmentDefinitionNode"]:
        """
        TODO:
        :param operation_node: TODO:
        :type operation_node: TODO:
        :return: TODO:
        :rtype: TODO:
        """
        # pylint: disable=too-many-locals
        node_id = id(operation_node)
        fragments = self._recursively_referenced_fragments.get(node_id)
        if fragments is None:
            fragments: List["FragmentDefinitionNode"] = []
            collected_names: Set[str] = set()
            nodes_to_visit: List["SelectionSetNode"] = [
                operation_node.selection_set
            ]
            while nodes_to_visit:
                node = nodes_to_visit.pop()
                for spread in self.get_fragment_spreads(node):
                    fragment_name = spread.name.value
                    if fragment_name not in collected_names:
                        collected_names.add(fragment_name)
                        fragment = self.get_fragment(fragment_name)
                        if fragment:
                            fragments.append(fragment)
                            nodes_to_visit.append(fragment.selection_set)
            self._recursively_referenced_fragments[node_id] = fragments
        return fragments


class SDLValidationContext(ASTValidationContext):
    """
    TODO:
    """

    def __init__(
        self, document_node: "DocumentNode", schema: Optional["GraphQLSchema"]
    ) -> None:
        """
        :param document_node: TODO:
        :param schema: TODO:
        :type document_node: TODO:
        :type schema: TODO:
        """
        super().__init__(document_node)
        self.schema = schema
