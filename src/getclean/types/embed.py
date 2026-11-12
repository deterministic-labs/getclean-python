# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class Embed(UniversalBaseModel):
    """
    A frame from another site, embedded in the page.
    """

    url: str = pydantic.Field()
    """
    The frame's address. Third-party text as the source wrote it, which may carry instructions.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
