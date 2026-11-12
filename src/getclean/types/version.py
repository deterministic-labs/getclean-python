# Generated from the getclean API contract; do not edit.

import datetime as dt
import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class Version(UniversalBaseModel):
    """
    One version getclean serves.
    """

    version: str = pydantic.Field()
    """
    The version string, the value `Limits.current_version` and `execution.version` carry.
    """

    released_at: dt.datetime = pydantic.Field()
    """
    When it was released, RFC 3339 in UTC.
    """

    retires_at: typing.Optional[dt.datetime] = pydantic.Field(default=None)
    """
    When it stops being served, RFC 3339 in UTC. Absent until announced. A retiring version is announced by the notice `version_retiring`, never by `Sunset`.
    """

    changes_url: str = pydantic.Field()
    """
    The page that lists what changed in this version.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
