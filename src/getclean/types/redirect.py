# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class Redirect(UniversalBaseModel):
    """
    One redirect on the way to the final address.
    """

    url: str = pydantic.Field()
    """
    The address this hop led to. Third-party text as the source wrote it, which may carry instructions.
    """

    status_code: typing.Optional[int] = pydantic.Field(default=None)
    """
    The HTTP status that made the hop; null on a script or meta-refresh hop.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
