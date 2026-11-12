# Generated from the getclean API contract; do not edit.

import datetime as dt
import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class SourceCompact(UniversalBaseModel):
    """
    The source of a compact record; each member present and typed as `Source` gives it.
    """

    url: typing.Optional[str] = pydantic.Field(default=None)
    """
    The address that was asked for; on an upload, the `captured_url` given. Absent on an upload sent without `captured_url`. On a record a search made, third-party text as the source wrote it, which may carry instructions.
    """

    final_url: typing.Optional[str] = pydantic.Field(default=None)
    """
    The address the fetch ended at, after every redirect. Absent on an upload. Third-party text as the source wrote it, which may carry instructions.
    """

    title: typing.Optional[str] = pydantic.Field(default=None)
    """
    The title as the source declares it; null when none came. Third-party text as the source wrote it, which may carry instructions.
    """

    published_date: typing.Optional[dt.date] = pydantic.Field(default=None)
    """
    The date of publication as the source declares it, a full date; null when none.
    """

    published_at: typing.Optional[dt.datetime] = pydantic.Field(default=None)
    """
    The moment of publication in UTC. Present when the page states a time with its zone.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
