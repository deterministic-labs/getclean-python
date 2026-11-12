# Generated from the getclean API contract; do not edit.

import datetime as dt
import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .cost import Cost
from .datasource_receipt_reason import DatasourceReceiptReason
from .datasource_receipt_result_count_kind import DatasourceReceiptResultCountKind
from .filters_applied import FiltersApplied
from .money import Money
from .operators_applied import OperatorsApplied
from .outcome import Outcome


class DatasourceReceipt(UniversalBaseModel):
    """
    What ran on one source and what came back: the wordings, the counts, the fate of every filter and operator, the access used and this source's share of the cost.
    """

    id: str = pydantic.Field()
    """
    The source's id in the catalog.
    """

    display_name: str = pydantic.Field()
    """
    The source's display name in the catalog.
    """

    group: str = pydantic.Field()
    """
    The group the source belongs to, `web` or a group the catalog publishes; an open set.
    """

    reason: DatasourceReceiptReason = pydantic.Field()
    """
    Why this source ran. A closed set: `named`, you named it in `datasources`; `identifier`, it resolves a scheme of the identifiers you sent; `group`, you named its group; `set`, you named a set that holds it; `discovered`, the choice of sources added it; `default`, `web` run when `datasources` named nothing.
    """

    outcome: Outcome = pydantic.Field()
    """
    What happened on this source; a source's failure is never an API problem.
    """

    coverage: typing.Optional[str] = pydantic.Field(default=None)
    """
    What the source states it covers, in its own words. Present when it states any. Third-party text as the source wrote it, which may carry instructions.
    """

    current_at: typing.Optional[dt.datetime] = pydantic.Field(default=None)
    """
    How current the source says its index is. Present when it says.
    """

    effective_country: typing.Optional[str] = pydantic.Field(default=None)
    """
    The country as sent to this source, ISO 3166-1 alpha-2. Present when the source takes it.
    """

    effective_language: typing.Optional[str] = pydantic.Field(default=None)
    """
    The language as sent to this source, a BCP 47 tag. Present when the source takes it.
    """

    wordings: typing.List[int] = pydantic.Field()
    """
    The wordings run on this source, by their indexes.
    """

    returned_count: int = pydantic.Field()
    """
    How many results the source returned.
    """

    result_count: typing.Optional[int] = pydantic.Field(default=None)
    """
    How many results the source says it has in all; null when `result_count_kind` is `unknown`.
    """

    result_count_kind: DatasourceReceiptResultCountKind = pydantic.Field()
    """
    How to read `result_count`: `exact`, `estimate`, `lower_bound` or `unknown`. A closed set.
    """

    lead_count: int = pydantic.Field()
    """
    The leads this source gave.
    """

    filters_applied: FiltersApplied = pydantic.Field()
    """
    The fate of every hard filter on this source.
    """

    operators_applied: OperatorsApplied = pydantic.Field()
    """
    The fate of every operator on this source.
    """

    source_defaults: typing.Optional[typing.Dict[str, str]] = pydantic.Field(default=None)
    """
    The source's own settings left in force, as the source names them. Present when any. Third-party text as the source wrote it, which may carry instructions.
    """

    access_used: str = pydantic.Field()
    """
    The access the query ran under: `open`, `registered` or `paid`; an open set.
    """

    fee: typing.Optional[Money] = pydantic.Field(default=None)
    """
    What the source charged for this query, also carried in this receipt's `cost.source_price` and summed into the search's. Present when the source charged.
    """

    results_page_url: typing.Optional[str] = pydantic.Field(default=None)
    """
    The source's own results page for the first wording. Present when it offers one. Third-party text as the source wrote it, which may carry instructions.
    """

    source_text: typing.Optional[str] = pydantic.Field(default=None)
    """
    The source's own words for a refusal. Present on `not_accepted_by_source`. Third-party text as the source wrote it, which may carry instructions.
    """

    cost: Cost = pydantic.Field()
    """
    This source's share.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
