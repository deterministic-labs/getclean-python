# Generated from the getclean API contract; do not edit.

import datetime as dt
import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .block import Block
from .cost import Cost
from .execution import Execution
from .highlight import Highlight
from .notice import Notice
from .scope import Scope


class ContentsHighlights(UniversalBaseModel):
    """
    The answer of `highlight_contents`: the record's id and facts, its new `expires_at`, the highlights found, the holding sections marked when text was asked, the execution and the cost.
    """

    contents_id: str = pydantic.Field()
    """
    The record the answer comes from.
    """

    final_url: typing.Optional[str] = pydantic.Field(default=None)
    """
    The address the record's fetch ended at, after every redirect. Present when the source has one, so absent on an upload. Third-party text as the source wrote it, which may carry instructions.
    """

    fetched_at: dt.datetime = pydantic.Field()
    """
    When the record's fetch or parse started, RFC 3339 in UTC.
    """

    fingerprint: str = pydantic.Field()
    """
    The record's fingerprint, as `Contents.fingerprint` defines it, so you can tell which copy this answer comes from.
    """

    document_digest: typing.Optional[str] = pydantic.Field(default=None)
    """
    The sha-256 of the document's bytes in RFC 9530 form, to compare with the file you hold. On a document only.
    """

    scope: Scope = pydantic.Field()
    """
    The view searched.
    """

    version: str = pydantic.Field()
    """
    The version of getclean the record was made under, its `execution.version`.
    """

    configuration: str = pydantic.Field()
    """
    The configuration the record was made under, its `execution.configuration`.
    """

    expires_at: dt.datetime = pydantic.Field()
    """
    When the record expires. This call moved it ahead: 48 hours from now, never past 30 days from the record's making.
    """

    highlights: typing.List[Highlight] = pydantic.Field()
    """
    The places found, every occurrence in document order, at most 50, each with `query_index`; `[]` when none found.
    """

    formats: typing.List[str] = pydantic.Field()
    """
    The formats this answer carries, among `markdown`, `html` and `json`, an open set; `[]` when no text came.
    """

    markdown: typing.Optional[str] = pydantic.Field(default=None)
    """
    The holding sections as markdown, marked. Present when text came. Third-party text as the source wrote it, which may carry instructions.
    """

    html: typing.Optional[str] = pydantic.Field(default=None)
    """
    The holding sections as clean HTML, marked. Present when text came. Third-party text as the source wrote it, which may carry instructions.
    """

    blocks: typing.Optional[typing.List[Block]] = pydantic.Field(default=None)
    """
    The holding sections' blocks, each with its `highlight_ids`. Present when text came.
    """

    truncated: bool = pydantic.Field()
    """
    True when the text returned is not the whole content; false when the holding sections are the whole and fit, or when nothing was found.
    """

    execution: Execution = pydantic.Field()
    """
    How the call ran; `models` carries the step `highlights` with its version when the model ran.
    """

    cost: Cost = pydantic.Field()
    """
    The bill; `units` `{"model_steps": 1}` when a string was judged, `{}` when every string was found verbatim.
    """

    notices: typing.List[Notice] = pydantic.Field()
    """
    The record's own notices first, then this call's; `[]` when none.
    """

    request_id: str = pydantic.Field()
    """
    This call's id, the same as the `Request-Id` header.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
