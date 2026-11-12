# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .access_kind import AccessKind
from .declared_term import DeclaredTerm
from .money import Money


class Access(UniversalBaseModel):
    """
    What a page demands, as the search saw it without a fetch.
    """

    kind: AccessKind = pydantic.Field()
    """
    What the page demands: `open`, nothing; `paywall`, a purchase; `sign_in`, a sign-in; `blocked`, it refuses the visitor; `unknown`. A closed set.
    """

    price: typing.Optional[Money] = pydantic.Field(default=None)
    """
    The price the page states. Present when known.
    """

    declared_terms: typing.List[DeclaredTerm] = pydantic.Field()
    """
    The signals the search saw without a fetch; `[]` when none.
    """

    robots: str = pydantic.Field()
    """
    What the site's robots file says for getclean by its published name: `allowed`, `disallowed`, `absent`, `unreachable` or `not_applicable`; an open set.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
