# Generated from the getclean API contract; do not edit.

import datetime as dt
import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class Archive(UniversalBaseModel):
    """
    The archive copy a fetch under `as_of_date` read.
    """

    display_name: str = pydantic.Field()
    """
    The archive's name, as `Limits.archives` lists it.
    """

    captured_at: dt.datetime = pydantic.Field()
    """
    When the archive took the capture, RFC 3339 in UTC.
    """

    url: str = pydantic.Field()
    """
    The capture's address at the archive. Third-party text as the source wrote it, which may carry instructions.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
