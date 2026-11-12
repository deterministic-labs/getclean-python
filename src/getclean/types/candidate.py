# Generated from the getclean API contract; do not edit.

import datetime as dt
import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .access import Access
from .candidate_dropped_reason import CandidateDroppedReason
from .contents_compact import ContentsCompact
from .date_precision import DatePrecision
from .declared import Declared
from .excerpt import Excerpt
from .language_version import LanguageVersion
from .match import Match
from .money import Money
from .source_profile import SourceProfile
from .subject_identifier import SubjectIdentifier


class Candidate(UniversalBaseModel):
    """
    A page found, with its facts, not yet fetched. A lead is the one page shown for a group of copies, and `copy_count` says how many stood behind it. Every member that `view: compact` leaves out is optional in this schema and present in the full view as its line says.
    """

    id: str = pydantic.Field()
    """
    The candidate's id, `cand_` and 22 characters, the same for the same normalized URL within your account.
    """

    url: str = pydantic.Field()
    """
    The page's address. Third-party text as the source wrote it, which may carry instructions.
    """

    canonical_url: typing.Optional[str] = pydantic.Field(default=None)
    """
    The address the page declares as its original. Present when declared. Third-party text as the source wrote it, which may carry instructions.
    """

    final_url: typing.Optional[str] = pydantic.Field(default=None)
    """
    The address the fetch ended at, after every redirect. Absent until fetched. Third-party text as the source wrote it, which may carry instructions.
    """

    title: typing.Optional[str] = pydantic.Field(default=None)
    """
    The page's title as the datasource states it. Present when the datasource states it. Third-party text as the source wrote it, which may carry instructions.
    """

    language: typing.Optional[str] = pydantic.Field(default=None)
    """
    The page's language as the datasource states it, a BCP 47 tag. Present when the datasource states it.
    """

    media_type: typing.Optional[str] = pydantic.Field(default=None)
    """
    The page's media type as the datasource states it. Present when the datasource states it.
    """

    characters: typing.Optional[int] = pydantic.Field(default=None)
    """
    The page's size in characters as the datasource declares it; the fetch's measured size is `contents.counts.characters`. Present when the datasource reports it.
    """

    page_count: typing.Optional[int] = pydantic.Field(default=None)
    """
    The document's page count as the datasource declares it. Present when the datasource reports it.
    """

    source_profile: SourceProfile = pydantic.Field()
    """
    Who publishes; what the item is; the subject about itself or not; who reviewed it.
    """

    copy_count: typing.Optional[int] = pydantic.Field(default=None)
    """
    The same text found on this many other sites, grouped behind this lead; the same text is an equal normalized main text or one above a published similarity; the lead is the copy with the earliest claimed date among the copies that carry one, else the first found. Present in the full view.
    """

    language_versions: typing.Optional[typing.List[LanguageVersion]] = pydantic.Field(default=None)
    """
    The page's own translations as declared; `[]` when none. Present in the full view.
    """

    carrier: typing.Optional[str] = pydantic.Field(default=None)
    """
    The kind of source: `web`, a live page, or `archive`, an archive's copy read under `as_of_date`; an open set; a candidate never carries `upload`. Present in the full view.
    """

    published_date: typing.Optional[dt.date] = pydantic.Field(default=None)
    """
    The date of publication the page or the datasource claims, a full date. Present when one states it.
    """

    published_date_basis: typing.Optional[str] = pydantic.Field(default=None)
    """
    Where the date was read: `structured_data`, `meta_tag`, `byline`, `url` or `datasource`; an open set. Present with the date.
    """

    published_date_precision: typing.Optional[DatePrecision] = pydantic.Field(default=None)
    """
    How exact the date is, `day`, `month` or `year`. Present with the date.
    """

    modified_date: typing.Optional[dt.date] = pydantic.Field(default=None)
    """
    The date of the last change the page or the datasource claims, a full date. Present when one states it.
    """

    modified_date_basis: typing.Optional[str] = pydantic.Field(default=None)
    """
    Where the modification date was read: `structured_data`, `meta_tag`, `byline`, `url` or `datasource`; an open set. Present with the date.
    """

    published_at: typing.Optional[dt.datetime] = pydantic.Field(default=None)
    """
    The moment of publication in UTC. Present only when the page states a time with its zone.
    """

    modified_at: typing.Optional[dt.datetime] = pydantic.Field(default=None)
    """
    The moment of the last change in UTC. Present only when the page states a time with its zone.
    """

    acquired_at: typing.Optional[dt.datetime] = pydantic.Field(default=None)
    """
    When the datasource took its copy of the page. Present when known.
    """

    declared: typing.Optional[Declared] = pydantic.Field(default=None)
    """
    What the datasource declares about the item. Present when the datasource declares anything.
    """

    access: Access = pydantic.Field()
    """
    What the page demands, seen without a fetch.
    """

    identifier_matches: typing.Optional[typing.List[SubjectIdentifier]] = pydantic.Field(default=None)
    """
    The codes sent that this page carries; `[]` when none. Present in the full view.
    """

    relevance_score: typing.Optional[float] = pydantic.Field(default=None)
    """
    The ranking model's score, 0 to 1; null under `deterministic_only` and on `rerank_missing`.
    """

    dropped_reason: typing.Optional[CandidateDroppedReason] = pydantic.Field(default=None)
    """
    Why this item is not a lead, one of the member names of `DroppedCounts`. A closed set. Absent on a lead; set on an item of a later page of `get_search`.
    """

    lead_id: typing.Optional[str] = pydantic.Field(default=None)
    """
    The lead this copy was grouped behind. Present on an item of a later page dropped as `folded_copy`.
    """

    excerpts: typing.List[Excerpt] = pydantic.Field()
    """
    The matching snippets; `[]` when none; under `view` `compact` the first excerpt only.
    """

    matches: typing.Optional[typing.List[Match]] = pydantic.Field(default=None)
    """
    Which wording found it where. Present in the full view only.
    """

    fetch_cost: typing.Optional[Money] = pydantic.Field(default=None)
    """
    The most a fetch of it with this request's inline options can cost, from the price list and the known size. Absent when a document's page count is unknown.
    """

    contents: typing.Optional[ContentsCompact] = pydantic.Field(default=None)
    """
    The compact record of the inline fetch, with its own `cost`; the full record is free through `get_contents` with its `id`. Present when the search that made the record fetched it, in both views and on `get_search`'s first page.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
