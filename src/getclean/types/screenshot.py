# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class Screenshot(UniversalBaseModel):
    """
    A picture of the whole page at the width it was read at, as PNG.
    """

    url: typing.Optional[str] = pydantic.Field(default=None)
    """
    Where to get the picture, a URL getclean serves for as long as the record lives, under `retention` `hold`.
    """

    data_base64: typing.Optional[str] = pydantic.Field(default=None)
    """
    The PNG bytes in base64, under `retention` `none`, where nothing is stored to serve; at most `bounds.contents.screenshot_bytes`.
    """

    digest: str = pydantic.Field()
    """
    The sha-256 of the PNG bytes in RFC 9530 form, so the picture can be proved unchanged.
    """

    width_px: int = pydantic.Field()
    """
    The width in pixels.
    """

    height_px: int = pydantic.Field()
    """
    The height in pixels.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
