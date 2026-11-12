# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class RecognizedPage(UniversalBaseModel):
    """
    One page read from its image, since it had no text layer.
    """

    page_number: int = pydantic.Field()
    """
    The page, counted from 1.
    """

    confidence: float = pydantic.Field()
    """
    How sure the recognition was of the page as a whole, 0 to 1.
    """

    image_url: typing.Optional[str] = pydantic.Field(default=None)
    """
    A picture of the page, at a URL getclean serves for as long as the record lives, so you can check the reading against the image. Absent under `retention` `none`.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
