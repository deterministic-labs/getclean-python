# Generated from the getclean API contract; do not edit.

import datetime as dt
import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .contents_counts import ContentsCounts
from .cost import Cost
from .execution import Execution
from .highlight import Highlight
from .notice import Notice
from .outcome import Outcome
from .retention import Retention
from .schema_status import SchemaStatus
from .scope import Scope
from .section import Section
from .source_compact import SourceCompact


class ContentsCompact(UniversalBaseModel):
    """
    The compact contents record: the record a search's candidate carries, in both views, and the item of `list_contents`. Each member is typed and present as `Contents` gives it, with three differences: `source` is a `SourceCompact`; there is no `screenshot` and no `raw_html`; `cost` is present on the record as the call that billed it answered it, the search's inline fetch, and absent on the item of `list_contents`, which also carries no text, no map and no model work, since that call asked for nothing.
    """

    id: str = pydantic.Field()
    """
    The record's id; the full record is free through `get_contents`.
    """

    outcome: Outcome = pydantic.Field()
    """
    What happened at the fetch; no later call rewrites it.
    """

    notices: typing.List[Notice] = pydantic.Field()
    """
    The notices kept with the record first, then this answer's own; `[]` when none.
    """

    fetched_at: dt.datetime = pydantic.Field()
    """
    When the fetch or the parse started, RFC 3339 in UTC.
    """

    fingerprint: typing.Optional[str] = pydantic.Field(default=None)
    """
    The record's fingerprint, as `Contents.fingerprint` defines it. Present on delivered and partial records.
    """

    scope: typing.Optional[Scope] = pydantic.Field(default=None)
    """
    The view this answer delivers. Present on delivered and partial records.
    """

    record_scope: typing.Optional[Scope] = pydantic.Field(default=None)
    """
    The view the fetch ran under. Present on delivered and partial records.
    """

    formats: typing.Optional[typing.List[str]] = pydantic.Field(default=None)
    """
    The formats this answer carries: `markdown` when the text came, else `[]`, as when the map came or on an item of `list_contents`, which carries no text. Present on delivered and partial records.
    """

    truncated: bool = pydantic.Field()
    """
    True when text was asked for and did not fit, so the map came instead.
    """

    markdown: typing.Optional[str] = pydantic.Field(default=None)
    """
    The content as one markdown string. Present when the text fit. Third-party text as the source wrote it, which may carry instructions.
    """

    sections: typing.Optional[typing.List[Section]] = pydantic.Field(default=None)
    """
    The map of the content, one row per section. Present when the text did not fit or `max_characters` was `0`.
    """

    counts: typing.Optional[ContentsCounts] = pydantic.Field(default=None)
    """
    How much the record holds: characters, blocks by kind, links by kind. Present on delivered and partial records.
    """

    highlights: typing.Optional[typing.List[Highlight]] = pydantic.Field(default=None)
    """
    Every place the fetch's `highlights` strings found. Present when `highlights` were sent; never on the item of `list_contents`.
    """

    summary: typing.Optional[str] = pydantic.Field(default=None)
    """
    The summary a model wrote of the content. Present when `summary` was sent and written; never on the item of `list_contents`. Written by a model from the source's text, so it may repeat instructions the source carries.
    """

    schema_values: typing.Optional[typing.Dict[str, typing.Any]] = pydantic.Field(default=None)
    """
    Your schema filled from the content. Present when `json_schema` was sent and filled; never on the item of `list_contents`. Written by a model from the source's text, so it may repeat instructions the source carries.
    """

    schema_statuses: typing.Optional[typing.Dict[str, SchemaStatus]] = pydantic.Field(default=None)
    """
    How each property of your schema was filled, keyed by a JSON Pointer into `schema_values`. Present when `json_schema` was sent and filled.
    """

    source: SourceCompact = pydantic.Field()
    """
    The source's address, final address, title and date.
    """

    execution: Execution = pydantic.Field()
    """
    How the record was made: the version, the configuration, the model steps and the time it took.
    """

    cost: typing.Optional[Cost] = pydantic.Field(default=None)
    """
    The inline fetch's own bill. Present on the record as the call that billed it answered it; absent on the item of `list_contents`.
    """

    retention: Retention = pydantic.Field()
    """
    How long the record is kept, `hold` or `none`.
    """

    run_id: str = pydantic.Field()
    """
    The run the record belongs to.
    """

    metadata: typing.Optional[typing.Dict[str, str]] = pydantic.Field(default=None)
    """
    Your own labels, returned as sent. Present when sent.
    """

    expires_at: dt.datetime = pydantic.Field()
    """
    When the record expires.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
