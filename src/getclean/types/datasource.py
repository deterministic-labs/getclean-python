# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .datasource_access import DatasourceAccess
from .filter_state import FilterState
from .operator_state import OperatorState


class Datasource(UniversalBaseModel):
    """
    One entry of the catalog: a place getclean can search, what it covers and what it honors, known before any search.
    """

    id: str = pydantic.Field()
    """
    The entry's id, the value the search's `datasources` takes.
    """

    display_name: str = pydantic.Field()
    """
    The entry's display name.
    """

    group: str = pydantic.Field()
    """
    The group the entry belongs to, `web` or a group the catalog publishes, an open set; a group name goes into the search's `datasources` too.
    """

    countries: typing.List[str] = pydantic.Field()
    """
    The countries it covers, ISO 3166-1 alpha-2; `[]` means every country, as `web`.
    """

    languages: typing.List[str] = pydantic.Field()
    """
    The languages it covers, BCP 47; `[]` means every language, as `web`.
    """

    access: DatasourceAccess = pydantic.Field()
    """
    How the source is reached, and its fee when it charges per query.
    """

    searchable: bool = pydantic.Field()
    """
    Whether getclean can search it; a source it cannot search is `datasource-not-searchable` when named.
    """

    filters: typing.Dict[str, FilterState] = pydantic.Field()
    """
    What the source honors of the twelve hard filters, before any search, keyed by their names, `allowed_domains`, `blocked_domains`, `published_from`, `published_until`, `published_within_days`, `undated`, `languages`, `media_types`, `safe_search`, `source_kinds`, `source_independence`, `as_of_date`, every name always present.
    """

    operators: typing.Dict[str, OperatorState] = pydantic.Field()
    """
    What the source honors of the ten query operators, keyed by `phrase`, `exclusion`, `alternatives`, `site`, `filetype`, `intitle`, `inurl`, `before`, `after`, `wildcard`, every name always present; `alternatives` stands for the `or` operator.
    """

    identifier_schemes: typing.List[str] = pydantic.Field()
    """
    The identifier schemes the source resolves, values of `SubjectIdentifier.scheme`; `[]` when none.
    """

    issuers: typing.Optional[typing.Dict[str, typing.List[str]]] = pydantic.Field(default=None)
    """
    For each scheme that takes an issuer, `ticker`, `docket`, `tax_id` and `registry`, the issuer codes this source resolves, so your agent learns a code from the catalog and never guesses one. Present when the source resolves such a scheme.
    """

    history: bool = pydantic.Field()
    """
    Whether `as_of_date` is honored; a source without history reports `no_history`.
    """

    card_url: str = pydantic.Field()
    """
    The entry's own page in the catalog, with its full description.
    """

    request_id: str = pydantic.Field()
    """
    The id of the call this entry came back in, the same as that call's `Request-Id` header.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
