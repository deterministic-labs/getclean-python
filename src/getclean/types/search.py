# Generated from the getclean API contract; do not edit.

import datetime as dt
import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .applied_search_request import AppliedSearchRequest
from .candidate import Candidate
from .cost import Cost
from .coverage_gap import CoverageGap
from .datasource_receipt import DatasourceReceipt
from .execution import Execution
from .interpretation import Interpretation
from .notice import Notice
from .outcome import Outcome
from .ranking import Ranking
from .retention import Retention
from .search_counts import SearchCounts
from .search_end_reason import SearchEndReason
from .search_record import SearchRecord


class Search(UniversalBaseModel):
    """
    One search record, `srch_`, kept 48 hours after its last call and at most 30 days from its making. It keeps the results and the receipt as they were, and `get_search` pages the list the search stored and never searches again or charges. It reads in one order: the outcome; the notices and the coverage gaps, read before the list; the leads in rank order with the facts of each; the counts, which describe the search and never a page; how the question was read and the request as it ran; the receipt per source; what ordered the list; how it ran; the money.

    Under `view` `compact` only these members come, each whole: `id`, `outcome`, `notices`, `coverage_gaps`, `counts`, `end_reason`, `cost`, `searched_at`, `run_id`, `expires_at`, `request_id`, `next_page_token` on a paged `get_search`, and `candidates`, each with `id`, `url`, `title`, `published_date`, `access`, `relevance_score`, `source_profile`, `fetch_cost`, `dropped_reason` on a paged item, `excerpts` holding the first excerpt only, and `contents` when fetched. Every member outside that list is optional in this schema and always present in the full view.
    """

    id: str = pydantic.Field()
    """
    The record's id, `srch_` and 22 random characters, which cannot be guessed.
    """

    retention: typing.Optional[Retention] = pydantic.Field(default=None)
    """
    How long the record is kept, `hold` or `none`. Present in the full view.
    """

    outcome: Outcome = pydantic.Field()
    """
    What happened, first. `delivered` when every source tried answered and everything asked ran, a source skipped before work being a coverage gap and no partial; `partial` when something tried did not finish; the other kinds only when no source answered.
    """

    notices: typing.List[Notice] = pydantic.Field()
    """
    Read before the list; a corrected query, an emulated filter, a cut, a default set by policy, a fetch that did not finish; a skipped source is a coverage gap, never a notice too. `[]` when none.
    """

    coverage_gaps: typing.List[CoverageGap] = pydantic.Field()
    """
    What was asked and not searched, with why; `[]` when none.
    """

    candidates: typing.List[Candidate] = pydantic.Field()
    """
    The leads, in rank order; `[]` when none. On a later page of `get_search`, the list the search stored, each item with `dropped_reason`.
    """

    counts: SearchCounts = pydantic.Field()
    """
    Leads returned and pages found before the cut; `found` equals `returned` plus every dropped count.
    """

    end_reason: typing.Optional[SearchEndReason] = pydantic.Field(default=None)
    """
    Why the list ended: `relevance`, the next candidate fell under the ranking model's cut-off; `max_candidates`, the cap on leads was reached; `ceiling`, the money ran out; `exhausted`, every source gave all it had; `source_cap`, every source reached `max_per_datasource`. A closed set. Present on `delivered` and `partial`, absent on the other kinds.
    """

    interpretation: typing.Optional[Interpretation] = pydantic.Field(default=None)
    """
    How the question was read. Present in the full view.
    """

    applied_request: typing.Optional[AppliedSearchRequest] = pydantic.Field(default=None)
    """
    The request as it ran; every field whose value was in force present with that value, defaults and resolutions written out; a field with no value absent. Present in the full view.
    """

    record: typing.Optional[SearchRecord] = pydantic.Field(default=None)
    """
    The search written up. Present only with `record_form`.
    """

    datasources_searched: typing.Optional[typing.List[DatasourceReceipt]] = pydantic.Field(default=None)
    """
    The receipt per source. Present in the full view, `[]` when none.
    """

    ranking: typing.Optional[Ranking] = pydantic.Field(default=None)
    """
    What ordered the list. Present in the full view.
    """

    execution: typing.Optional[Execution] = pydantic.Field(default=None)
    """
    How it ran; `models` carries `reranking`, `discovery` and `source_profile` when they ran. Present in the full view.
    """

    cost: Cost = pydantic.Field()
    """
    The money, the original bill as stored on every `get_search` page, never a new charge; `units` among `searches`, `datasource_queries`, `model_steps` and the inline fetches' units.
    """

    metadata: typing.Optional[typing.Dict[str, str]] = pydantic.Field(default=None)
    """
    Your own labels, returned as sent. Present when sent.
    """

    searched_at: dt.datetime = pydantic.Field()
    """
    When the search started, RFC 3339 in UTC.
    """

    run_id: str = pydantic.Field()
    """
    The run the record belongs to.
    """

    expires_at: dt.datetime = pydantic.Field()
    """
    When the record expires. This call moved it ahead, 48 hours from now, never past 30 days from the record's making; under `retention` `none` it is this answer's own moment. After that a call on the record is `410 search-expired` for 30 days, then `404`.
    """

    request_id: str = pydantic.Field()
    """
    This call's id, the same as the `Request-Id` header.
    """

    next_page_token: typing.Optional[str] = pydantic.Field(default=None)
    """
    The token for the next page of the list the search stored; pass it to `get_search` as `page_token`. Present only on a paged `get_search` while more remains, and a page that carries it always has at least one result.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
