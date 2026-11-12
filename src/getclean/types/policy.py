# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .retention import Retention
from .safe_search import SafeSearch


class Policy(UniversalBaseModel):
    """
    The key's settings and minimums, set by the account owner. A request may tighten them for one call and never loosen them.
    """

    deterministic_only: bool = pydantic.Field()
    """
    True when the policy forbids model work. Every call then runs as if it sent `deterministic_only` true, with the notice `default_set_by_policy`.
    """

    safe_search: SafeSearch = pydantic.Field()
    """
    The floor a search's `safe_search` may not go below.
    """

    retention: Retention = pydantic.Field()
    """
    The account's retention mode, `hold` on a new account. A request may shorten it to `none` for one call, never lengthen it.
    """

    allowed_domains: typing.List[str] = pydantic.Field()
    """
    The hosts a fetch may reach and a search may count, every redirect hop included; `[]` when none is set.
    """

    blocked_domains: typing.List[str] = pydantic.Field()
    """
    The hosts a fetch never reaches and a search never counts; `[]` when none is set.
    """

    refuse_credential_urls: bool = pydantic.Field()
    """
    True when a URL whose query carries a parameter named `token`, `key`, `password`, `session`, `auth`, `sig` or `signature`, or any userinfo, is refused before work; off by default.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
