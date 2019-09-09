from typing import Any, List

from tartiflette.language.visitor.constants import BREAK, OK, SKIP
from tartiflette.language.visitor.utils import get_visit_function


class Visitor:
    """
    TODO:
    """


class ParallelVisitor(Visitor):
    """
    TODO:
    """

    def __init__(self, visitors: List["Visitor"]) -> None:
        """
        :param visitors: TODO:
        :type visitors: TODO:
        """
        self.visitors = visitors
        self.skipping: List[Any] = [None] * len(visitors)

    def enter(  # pylint: disable=inconsistent-return-statements
        self, node, key, parent, path, ancestors
    ):
        """
        TODO:
        :param node: TODO:
        :param key: TODO:
        :param parent: TODO:
        :param path: TODO:
        :param ancestors: TODO:
        :type node: TODO:
        :type key: TODO:
        :type parent: TODO:
        :type path: TODO:
        :type ancestors: TODO:
        :return: TODO:
        :rtype: TODO:
        """
        # pylint: disable=too-many-locals
        for i, visitor in enumerate(self.visitors):
            if not self.skipping[i]:
                fn = get_visit_function(visitor, node)
                if fn:
                    result = fn(node, key, parent, path, ancestors)
                    if result is SKIP:
                        self.skipping[i] = node
                    elif result is BREAK:
                        self.skipping[i] = BREAK
                    elif result is not OK:
                        return result

    def leave(  # pylint: disable=inconsistent-return-statements
        self, node, key, parent, path, ancestors
    ):
        """
        TODO:
        :param node: TODO:
        :param key: TODO:
        :param parent: TODO:
        :param path: TODO:
        :param ancestors: TODO:
        :type node: TODO:
        :type key: TODO:
        :type parent: TODO:
        :type path: TODO:
        :type ancestors: TODO:
        :return: TODO:
        :rtype: TODO:
        """
        # pylint: disable=too-many-locals
        for i, visitor in enumerate(self.visitors):
            if not self.skipping[i]:
                fn = get_visit_function(visitor, node, is_leaving=True)
                if fn:
                    result = fn(node, key, parent, path, ancestors)
                    if result is BREAK:
                        self.skipping[i] = BREAK
                    elif result is not OK and result is not SKIP:
                        return result
            elif self.skipping[i] is node:
                self.skipping[i] = None
