# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class PicturedPage(UniversalBaseModel):
    """
    One page that holds content the text cannot carry, with a picture of it.
    """

    page_number: int = pydantic.Field()
    """
    The page, counted from 1.
    """

    kind: str = pydantic.Field()
    """
    What the page holds, an open set: `handwriting`, `drawing`, `formula`, `redaction`.
    """

    image_url: typing.Optional[str] = pydantic.Field(default=None)
    """
    A picture of the page, at a URL getclean serves for as long as the record lives. Absent under `retention` `none`.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
