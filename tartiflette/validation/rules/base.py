from tartiflette.language.visitor.visitor import Visitor


class ASTValidationRule(Visitor):
    """
    TODO:
    """

    def __init__(self, context: "ASTValidationContext") -> None:
        """
        :param context: TODO:
        :type context: TODO:
        """
        self.context = context
