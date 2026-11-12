# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class TimeStamp(UniversalBaseModel):
    """
    Proof that the record existed at a moment: an RFC 3161 time-stamp token over one datum, the sha-256 of the record's fingerprint followed by the screenshot's digest, or of the fingerprint alone when no screenshot was made.
    """

    token: str = pydantic.Field()
    """
    The token, in base64.
    """

    authority: str = pydantic.Field()
    """
    The name of the time-stamping authority that issued it.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
