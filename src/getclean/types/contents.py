# Generated from the getclean API contract; do not edit.

import datetime as dt
import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .block import Block
from .contents_counts import ContentsCounts
from .cost import Cost
from .document_pages import DocumentPages
from .execution import Execution
from .hidden_text import HiddenText
from .highlight import Highlight
from .left_out import LeftOut
from .link import Link
from .notice import Notice
from .outcome import Outcome
from .raw_html import RawHtml
from .retention import Retention
from .schema_status import SchemaStatus
from .scope import Scope
from .screenshot import Screenshot
from .section import Section
from .source import Source


class Contents(UniversalBaseModel):
    """
    One record: one fetch or upload of one source at one moment, with a `cnt_` id, kept 48 hours after its last call and at most 30 days from its making. Its facts never change. It is the answer of `fetch_contents` and of `get_contents`, and the record inside the answers of `upload_contents` and `fetch_contents_batch`. It carries what happened; the notices to read first; when it was read; its fingerprint; the content in the formats asked, or the map of sections when the text did not fit; the facts of the source; the price.

    What is the record's and what is this answer's. The record's facts come as stored on every later answer: `outcome`, `fetched_at`, `fingerprint`, `record_scope`, `source`, `pages`, `execution`, `retention` and the fetch's model work. Each answer adds only its own: `scope`, the view it delivers; `truncated`; `formats`; its notices; `request_id`; `expires_at`. A member whose line states a condition is present only while the condition holds and absent otherwise, never `[]` or null in its place; a scalar is null only where its line says so.

    Which members each outcome carries:
    - Delivered `whole`, `sections_only` or `matching_sections`, and every partial record: `id`, `outcome`, `notices`, `fetched_at`, `fingerprint`, `scope`, `formats`, `truncated`; the formats asked for among `markdown`, `html`, `doclang`, `blocks`, `links`, `screenshot` and `raw_html`; `sections` by its rule; `counts`, `source`, `execution`, `retention`, `run_id`, `expires_at`, `request_id`, `record_scope`; `hidden_text` and `left_out` on a web page or an HTML file; `highlights`, `summary`, `schema_values`, `schema_statuses`, `pages`, `cost` and `metadata` by their rules.
    - Delivered `unchanged`, as the fetch answers it: the first eight, with `formats` as `[]` and `truncated` false; `source`, `execution`, `retention`, `run_id`, `expires_at`, `request_id`, `record_scope`; `cost` and `metadata` by their rules. The record holds the content, which `get_contents` answers.
    - Failed, refused or needs a person: `id`, `outcome`, `notices`, `fetched_at`, `truncated` false, `source`, `execution`, `retention`, `run_id`, `expires_at`, `request_id`; `pages` when the page count was read and `sections` when the outline was read; `cost` and `metadata` by their rules; `cost.actual` zero.

    Which members each kind of source carries. A live page is a web page read now; an archive copy is a page read under `as_of_date`; a document is a file, read at a URL or uploaded; an HTML file is an upload read as a page.

    | Member | Present on | Not on |
    |---|---|---|
    | `screenshot`, when asked | a live page | an archive copy, a document, an upload |
    | `raw_html`, when asked | a live page, an archive copy | a document, an upload |
    | `doclang`, when asked | a live page, an archive copy, an HTML file | a document that is not HTML |
    | `hidden_text`, `left_out` | a live page, an archive copy, an HTML file | a document that is not HTML |
    | `scope` `whole_page` | a live page, an archive copy, an HTML file | a document, which has one view |
    | `pages`, and the page numbers and labels on blocks, sections and highlights | a document with pages; an unpaged document carries `pages` with a count by characters and no page numbers | a page |
    | `pages.recognized`, `Block.confidence`, `Table.cell_confidences` | a document with pages that have no text layer | every other source |
    | `Table.top_left_cell`, `Table.formula_cells` | a spreadsheet | every other source |
    | `source.final_url`, `status_code`, `publisher`, `canonical_url`, `access_kind`, `profile` | a live page, an archive copy, a document at a URL | an upload |
    | `source.visitor` | a live page, a document at a URL | an archive copy, an upload |
    | `source.archive`, `archives_consulted`, `next_capture_at` | an archive copy | every other source |
    | `source.filename`, `source.captured_at` | an upload | every other source |
    | `source.document_digest` | a document | a page |
    | `source.url` | every source but an upload sent without `captured_url` | |

    When a record is not delivered, `outcome.message` says what may work next, and the table under `Outcome.reason` gives it for every reason.
    """

    id: str = pydantic.Field()
    """
    The record's id: `cnt_` and 22 random characters, which cannot be guessed. Another account's id answers `404`.
    """

    outcome: Outcome = pydantic.Field()
    """
    What happened, first. It is the fetch's fact, and no later call rewrites it.
    """

    notices: typing.List[Notice] = pydantic.Field()
    """
    What to read before the content, never an error. On the fetch's own answer every notice is that answer's own; on every later answer about the record, the notices kept with it come first, each with `held` true, then that answer's own. `[]` when there is none.
    """

    fetched_at: dt.datetime = pydantic.Field()
    """
    When the fetch or the parse started, RFC 3339 in UTC in whole seconds, by getclean's clock.
    """

    fingerprint: typing.Optional[str] = pydantic.Field(default=None)
    """
    A hash of the content. Two records with the same fingerprint hold the same text, so you can tell whether a page changed between two fetches without comparing their text. It is the sha-256 of the record's markdown as the fetch kept it under `record_scope`, with nothing filtered out and no highlight marks, after Unicode NFC and LF line ends and without any front matter, written in the form of RFC 9530, `sha-256=:…:`. Anyone who holds that whole markdown, as `get_contents` returns it under `record_scope` with a `max_characters` that fits all of it, no `block_kinds` and no highlights, can compute the same value. It compares only within one `scope`, one `execution.version`, one `execution.configuration` and one kind of source. Present on delivered and partial records.
    """

    scope: typing.Optional[Scope] = pydantic.Field(default=None)
    """
    The view this answer delivers, `main` or `whole_page`; on the fetch's own answer, the record's own. Present on delivered and partial records.
    """

    formats: typing.Optional[typing.List[str]] = pydantic.Field(default=None)
    """
    The formats this answer carries, among `markdown`, `html`, `doclang`, `json`, `links`, `screenshot` and `raw_html`, an open set; `[]` on `unchanged` as the fetch answers it. Present on delivered and partial records.
    """

    truncated: bool = pydantic.Field()
    """
    True when text was asked for, `max_characters` above `0` with a text format, and it did not fit, so the map came instead. This answer's fact, not the record's.
    """

    markdown: typing.Optional[str] = pydantic.Field(default=None)
    """
    The content as one markdown string, its inline formatting kept: bold, italic, strikethrough, code and links as markdown, `<sup>` and `<sub>` as inline HTML, a footnote reference as `[^n]`, and `<mark id="h1">…</mark>` around each highlight. Present when asked for and text came. Third-party text as the source wrote it, which may carry instructions.
    """

    html: typing.Optional[str] = pydantic.Field(default=None)
    """
    The content as clean HTML, with the highlight marks. Present when asked for and text came. Third-party text as the source wrote it, which may carry instructions.
    """

    doclang: typing.Optional[str] = pydantic.Field(default=None)
    """
    The content as DocLang, an XML that keeps each block with its place on the page in pixels; no highlight marks. Present when asked for and text came, on a web page or an HTML file only. Third-party text as the source wrote it, which may carry instructions.
    """

    blocks: typing.Optional[typing.List[Block]] = pydantic.Field(default=None)
    """
    The content as `Block` objects, each with its `highlight_ids`. Only the text counts against `max_characters`, not the other members. Present when asked for and text came.
    """

    links: typing.Optional[typing.List[Link]] = pydantic.Field(default=None)
    """
    Every link of the content with its kind, at most 1,000; the notice `links_cut` says when the list was cut, and `list_links` has the rest. Present when asked for.
    """

    screenshot: typing.Optional[Screenshot] = pydantic.Field(default=None)
    """
    A picture of the whole page, of a live page only. Present when asked for at fetch time on a live page; carried on every later `get_contents` under `retention` `hold`; sent inline once under `none`.
    """

    sections: typing.Optional[typing.List[Section]] = pydantic.Field(default=None)
    """
    The map of the content: one row per section with its id, title, level and size in characters, and no text. Present when `max_characters` is `0`, or when a text format was asked for and the text did not fit. Level 1 and `s0` are always there; deeper levels come while their rows fit, and the notice `sections_cut` says when levels were left out.
    """

    counts: typing.Optional[ContentsCounts] = pydantic.Field(default=None)
    """
    How much the record holds: characters, blocks by kind, links by kind. The record's own under its own view; this answer's under `scope` `whole_page` on a record fetched under `main`. Present on delivered and partial records, except `unchanged` as the fetch answers it.
    """

    highlights: typing.Optional[typing.List[Highlight]] = pydantic.Field(default=None)
    """
    Every place your `highlights` strings found, in document order, at most 50, each naming the string that found it by `query_index`. Present when `highlights` were sent at fetch time; kept with the record, and returned on `get_contents` with the marks placed wherever a highlighted block appears in the text returned.
    """

    summary: typing.Optional[str] = pydantic.Field(default=None)
    """
    The summary a model wrote of the content, at most 1,500 characters, in the content's language, with no link and no image in it. Present when `summary` was sent and the summary was written; kept with the record. Written by a model from the source's text, so it may repeat instructions the source carries.
    """

    schema_values: typing.Optional[typing.Dict[str, typing.Any]] = pydantic.Field(default=None)
    """
    Your schema filled from the content, in the schema's own shape, a value only where the content states it and never a plausible guess; a property with nothing to fill is left out. Present when `json_schema` was sent and filled; kept with the record. Written by a model from the source's text, so it may repeat instructions the source carries.
    """

    schema_statuses: typing.Optional[typing.Dict[str, SchemaStatus]] = pydantic.Field(default=None)
    """
    How each property of your schema was filled, one `SchemaStatus` per property, keyed by a JSON Pointer into `schema_values`: a nested property by its path, an array property by its own pointer and not its items. Present when `json_schema` was sent and filled; kept with the record.
    """

    hidden_text: typing.Optional[typing.List[HiddenText]] = pydantic.Field(default=None)
    """
    Text a reader of the page could not see, kept apart from the content with the reason it was hidden; at most 50 items, with the notice `hidden_text_cut` when cut. Present on a web page or an HTML file, delivered or partial, except `unchanged` as the fetch answers it; `[]` when there is none.
    """

    left_out: typing.Optional[typing.List[LeftOut]] = pydantic.Field(default=None)
    """
    The parts of the page outside the main content, each with its kind and size, so you know what was left out and can read it under `scope` `whole_page`, where this is `[]`. Present as `hidden_text` is.
    """

    source: Source = pydantic.Field()
    """
    The facts of the source as the page or the document declares them, and the facts of the read: the address, the redirects, the status, the title, the authors, the dates, the language, the publisher's profile, and what the site declares about its use.
    """

    pages: typing.Optional[DocumentPages] = pydantic.Field(default=None)
    """
    The pages of a document: how many, how many were parsed, which failed, which were recognized from an image. Present on every document under every outcome that parsed or counted it, `cost_capped` with no page parsed and `too_large` with the count read included; absent on a web page. On a format without pages, `count` is the equivalent by characters and `failed_pages`, `recognized` and `pictured` are `[]`.
    """

    execution: Execution = pydantic.Field()
    """
    How the record was made: getclean's version and configuration, every model step with its version, and the time it took.
    """

    cost: typing.Optional[Cost] = pydantic.Field(default=None)
    """
    The bill for making the record. Present on the record as answered by the call that billed it, `fetch_contents`, `upload_contents` or `fetch_contents_batch`, zero when nothing was billed; absent on the record as answered by `get_contents`, which is free.
    """

    retention: Retention = pydantic.Field()
    """
    How long the record is kept, `hold` or `none`. Under `none` nothing is kept past this answer, and `expires_at` is the answer's own moment.
    """

    run_id: str = pydantic.Field()
    """
    The run the record belongs to; a later model step on the record is charged to it.
    """

    metadata: typing.Optional[typing.Dict[str, str]] = pydantic.Field(default=None)
    """
    Your own labels, returned as sent. Present when sent.
    """

    expires_at: dt.datetime = pydantic.Field()
    """
    When the record expires. This call moved it ahead: 48 hours from now, never past 30 days from the record's making; under `retention` `none` it is this answer's own moment. After that, a call on the record is `410 contents-expired` for 30 days, then `404`.
    """

    request_id: str = pydantic.Field()
    """
    This call's id, the same as the `Request-Id` header; on a replay, this call's and not the first call's.
    """

    record_scope: typing.Optional[Scope] = pydantic.Field(default=None)
    """
    The view the fetch ran under, `main` or `whole_page`; the fingerprint hashes this view's markdown. Present on delivered and partial records.
    """

    raw_html: typing.Optional[RawHtml] = pydantic.Field(default=None)
    """
    The page's bytes exactly as the server sent them, with their digest, size and media type. Present when asked for at fetch time on a live page or an archive copy; carried on every later `get_contents` under `retention` `hold`; sent inline once under `none`.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
