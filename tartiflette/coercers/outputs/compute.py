from functools import partial
from typing import Callable

from tartiflette.coercers.outputs.list_coercer import list_coercer
from tartiflette.coercers.outputs.non_null_coercer import non_null_coercer

__all__ = ("get_output_coercer",)


def get_output_coercer(graphql_type: "GraphQLType") -> Callable:
    """
    Computes and returns the output coercer to use for the filled in schema
    type.
    :param graphql_type: the schema type for which compute the coercer
    :type graphql_type: GraphQLType
    :return: the computed coercer wrap with directives if defined
    :rtype: Callable
    """
    inner_type = graphql_type
    wrapper_coercers = []
    while inner_type.is_wrapping_type:
        wrapped_type = inner_type.wrapped_type
        if inner_type.is_list_type:
            wrapper_coercers.append(
                partial(list_coercer, item_type=wrapped_type)
            )
        elif inner_type.is_non_null_type:
            wrapper_coercers.append(non_null_coercer)
        inner_type = wrapped_type

    try:
        coercer = inner_type.output_coercer
    except AttributeError:
        # This case should never happen and raise an exception at schema
        # validation time.
        coercer = lambda *args, **kwargs: None

    for wrapper_coercer in reversed(wrapper_coercers):
        coercer = partial(wrapper_coercer, inner_coercer=coercer)

    return coercer
