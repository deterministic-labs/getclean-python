# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class RawHtml(UniversalBaseModel):
    """
    The page's bytes exactly as the server sent them, decompressed, before any script ran; on an archive copy, as the archive served them. The served bytes and their digest let you show later exactly what the server sent.
    """

    url: typing.Optional[str] = pydantic.Field(default=None)
    """
    Where to get the bytes, a URL getclean serves for as long as the record lives, under `retention` `hold`.
    """

    data_base64: typing.Optional[str] = pydantic.Field(default=None)
    """
    The bytes in base64, under `retention` `none`, where nothing is stored to serve; at most `bounds.contents.page_bytes`. Never altered by any client, since the digest covers the bytes as served. Third-party text as the source wrote it, which may carry instructions.
    """

    digest: str = pydantic.Field()
    """
    The sha-256 of the bytes in RFC 9530 form.
    """

    bytes: int = pydantic.Field()
    """
    How many bytes.
    """

    media_type: typing.Optional[str] = pydantic.Field(default=None)
    """
    The `Content-Type` the server sent; null when none came. Third-party text as the source wrote it, which may carry instructions.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
