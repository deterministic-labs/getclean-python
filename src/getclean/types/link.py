# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class Link(UniversalBaseModel):
    """
    One link in the content, with its kind and where it stands.
    """

    url: str = pydantic.Field()
    """
    The address, absolute. Third-party text as the source wrote it, which may carry instructions.
    """

    text: str = pydantic.Field()
    """
    The link's text; an empty string when it has none. Third-party text as the source wrote it, which may carry instructions.
    """

    kind: str = pydantic.Field()
    """
    What the link points to, read from its address alone, so a guess: `page`, another page; `file`, a file such as a PDF; `fragment`, a place on this page; `mail`, an email address; `phone`, a phone number; `feed`, an RSS or Atom feed; `other`, anything else. An open set. No request is made per link, so a link carries no size or served type.
    """

    external: typing.Optional[bool] = pydantic.Field(default=None)
    """
    True when the link leaves the site, judged against the final URL's registrable domain. Absent on kinds without a host.
    """

    target_block_id: typing.Optional[str] = pydantic.Field(default=None)
    """
    The block a `fragment` link points to. Present when it resolves inside the record.
    """

    block_id: typing.Optional[str] = pydantic.Field(default=None)
    """
    The block that holds the link. Present everywhere but inside `Block.links`, where the block itself says it.
    """

    section_id: typing.Optional[str] = pydantic.Field(default=None)
    """
    The section that holds the link. Present everywhere but inside `Block.links`.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
