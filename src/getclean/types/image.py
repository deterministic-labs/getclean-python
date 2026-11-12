# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class Image(UniversalBaseModel):
    """
    An image in the content.
    """

    url: typing.Optional[str] = pydantic.Field(default=None)
    """
    Where to get the image: its own address as the page gives it, or a URL getclean serves for an image inside a document. Absent on a document's image under `retention` `none`. On a web image, third-party text as the source wrote it, which may carry instructions; on a document's image, getclean's own URL.
    """

    digest: typing.Optional[str] = pydantic.Field(default=None)
    """
    The sha-256 of the image's bytes in RFC 9530 form, so two images can be told equal; null when the bytes were not loaded.
    """

    alt: typing.Optional[str] = pydantic.Field(default=None)
    """
    The image's alternative text; null when it has none. Third-party text as the source wrote it, which may carry instructions.
    """

    caption: typing.Optional[str] = pydantic.Field(default=None)
    """
    The caption the source ties to the image; null when there is none. Third-party text as the source wrote it, which may carry instructions.
    """

    width_px: int = pydantic.Field()
    """
    The width as the page shows it, in CSS pixels, rounded; the image's own pixel width in a document.
    """

    height_px: int = pydantic.Field()
    """
    The height, measured as `width_px` is.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
