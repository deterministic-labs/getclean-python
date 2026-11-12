# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class ContentsCounts(UniversalBaseModel):
    """
    How much a record holds under one view: characters, blocks by kind and links by kind.
    """

    characters: int = pydantic.Field()
    """
    The content's text in characters.
    """

    blocks: typing.Dict[str, int] = pydantic.Field()
    """
    How many blocks of each kind, keyed by kind: `text`, `heading`, `code`, `math`, `divider`, `interactive`, `table`, `image`, `embed`, `media`, an open set. `{}` when there is none.
    """

    links: typing.Dict[str, int] = pydantic.Field()
    """
    How many links of each kind, keyed by kind: `page`, `file`, `fragment`, `mail`, `phone`, `feed`, `other`, an open set. `{}` when there is none.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
