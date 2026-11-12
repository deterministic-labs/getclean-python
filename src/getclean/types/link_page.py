# Generated from the getclean API contract; do not edit.

import datetime as dt
import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .link import Link
from .notice import Notice
from .scope import Scope


class LinkPage(UniversalBaseModel):
    """
    One page of a record's links, the answer of `list_links`. First the record's id and facts, and the record's new `expires_at`; then the links, each with its kind and its place; then `next_page_token` while more remain.
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

    links: typing.List[Link] = pydantic.Field()
    """
    The links of this page, each with its kind and its `block_id` and `section_id`; `[]` when none matches.
    """

    next_page_token: typing.Optional[str] = pydantic.Field(default=None)
    """
    The token for the next page; pass it as `page_token`. Present while more remains, and a page that carries it always has at least one link.
    """

    notices: typing.List[Notice] = pydantic.Field()
    """
    The record's own notices first, then this call's own: `page_size_lowered`, `field_not_applicable`, `version_retiring`. `[]` when there is none.
    """

    request_id: str = pydantic.Field()
    """
    This call's id, the same as the `Request-Id` header.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
