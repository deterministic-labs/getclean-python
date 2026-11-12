# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .bounds import Bounds
from .caps import Caps
from .money import Money
from .policy import Policy
from .rates import Rates
from .usage import Usage
from .version import Version


class Limits(UniversalBaseModel):
    """
    Your key's limits and your account's money, the answer of `get_limits`. Read it once before a batch or a long run: every price, bound and default you may meet stands here. It is the key's own and is never cached.
    """

    balance: Money = pydantic.Field()
    """
    Prepaid credit left, after the sums reserved by calls in flight.
    """

    usage: Usage = pydantic.Field()
    """
    What the account has used in its current billing period, from `starts_at` to `ends_at`.
    """

    prices: typing.Dict[str, Money] = pydantic.Field()
    """
    Every unit's price, keyed by unit name: `contents`, `model_steps`, `screenshots`, `document_pages`, `recognized_pages`, `searches` and `datasource_queries`, an open set.
    """

    caps: Caps = pydantic.Field()
    """
    The key's cap on one call, the default run's budget and the key's budget.
    """

    rates: Rates = pydantic.Field()
    """
    The key's rate: requests per minute, calls in flight at once, and when the minute's window resets; one rate for every operation.
    """

    bounds: Bounds = pydantic.Field()
    """
    The published bounds of both families: every request field's range and default, and the service's own limits.
    """

    document_media_types: typing.List[str] = pydantic.Field()
    """
    The document types the upload and a document at a URL take, as IANA media types. The families: the Office formats old and new, ODF, PDF, EPUB, RTF, Markdown, CSV and HWP, with HTML, XHTML, XML, JSON, YAML, plain text and source files. This list is the exact set.
    """

    exits: typing.List[str] = pydantic.Field()
    """
    The countries `subject_country` may name on a fetch, ISO 3166-1 alpha-2.
    """

    recognition_languages: typing.List[str] = pydantic.Field()
    """
    The languages text recognition can be asked for on a page with no text layer, BCP 47 tags; another is refused `not_allowed`.
    """

    archives: typing.List[str] = pydantic.Field()
    """
    The archives an as-of fetch consults, by display name.
    """

    default_exit: str = pydantic.Field()
    """
    The country a fetch is made from when it names none, ISO 3166-1 alpha-2.
    """

    policy: Policy = pydantic.Field()
    """
    The key's settings and minimums, set by the account owner.
    """

    versions: typing.List[Version] = pydantic.Field()
    """
    Every version served, each with its release and, once announced, its retirement.
    """

    current_version: str = pydantic.Field()
    """
    The version a request without `pinned_version` runs under.
    """

    version_minimum_days: int = pydantic.Field()
    """
    The least number of days a version and its configuration keep being served after their change is announced.
    """

    request_id: str = pydantic.Field()
    """
    This call's id, the same as the `Request-Id` header.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
