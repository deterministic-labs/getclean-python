# Generated from the getclean API contract; do not edit.

import datetime as dt
import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .block import Block
from .link import Link
from .notice import Notice
from .scope import Scope
from .section import Section


class SectionContents(UniversalBaseModel):
    """
    One section of a record, the answer of `get_section`. First the id and facts of the record the section comes from, and its new `expires_at`; then the section's row; then its text in the formats asked for, or its child rows when the whole section did not fit.
    """

    contents_id: str = pydantic.Field()
    """
    The record the answer comes from.
    """

    final_url: typing.Optional[str] = pydantic.Field(default=None)
    """
    The address the record's fetch ended at. Present when the source has one, so absent on an upload. Third-party text as the source wrote it, which may carry instructions.
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
    The view this answer delivers, `main` or `whole_page`.
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

    section: Section = pydantic.Field()
    """
    The section's own row of the map: its id, title, level and size.
    """

    formats: typing.List[str] = pydantic.Field()
    """
    The formats this answer carries, among `markdown`, `html`, `doclang`, `json` and `links`, an open set. Under `max_characters` `0` only `links` when asked for, else `[]`.
    """

    markdown: typing.Optional[str] = pydantic.Field(default=None)
    """
    The section's text as markdown, its inline formatting kept. Present when asked for and text came. Third-party text as the source wrote it, which may carry instructions.
    """

    html: typing.Optional[str] = pydantic.Field(default=None)
    """
    The section's text as clean HTML. Present when asked for and text came. Third-party text as the source wrote it, which may carry instructions.
    """

    doclang: typing.Optional[str] = pydantic.Field(default=None)
    """
    The section's text as DocLang XML. Present when asked for and text came, on a web page or an HTML file only. Third-party text as the source wrote it, which may carry instructions.
    """

    blocks: typing.Optional[typing.List[Block]] = pydantic.Field(default=None)
    """
    The section's blocks. Present when asked for and text came.
    """

    links: typing.Optional[typing.List[Link]] = pydantic.Field(default=None)
    """
    The section's links, narrowed by `block_kinds`, each with its `block_id` and `section_id`. Present when asked for, under `max_characters` `0` too.
    """

    truncated: bool = pydantic.Field()
    """
    True when the whole section did not fit `max_characters`, so its text was cut or its child rows came in place of their text.
    """

    next_page_token: typing.Optional[str] = pydantic.Field(default=None)
    """
    The token that continues a cut text; pass it as `page_token`. Present while more remains, and a page that carries it always has text.
    """

    sections: typing.Optional[typing.List[Section]] = pydantic.Field(default=None)
    """
    The rows of the sections under this one. Present when the whole section did not fit, on the first page only, or under `max_characters` `0`.
    """

    notices: typing.List[Notice] = pydantic.Field()
    """
    The record's own notices first, then this call's own: `sections_cut`, `links_cut`, `field_not_applicable`, `version_retiring`. `[]` when there is none.
    """

    request_id: str = pydantic.Field()
    """
    This call's id, the same as the `Request-Id` header.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
