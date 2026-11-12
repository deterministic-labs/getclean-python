# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class Media(UniversalBaseModel):
    """
    An audio or video file in the content.
    """

    url: str = pydantic.Field()
    """
    The media file's address. Third-party text as the source wrote it, which may carry instructions.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
