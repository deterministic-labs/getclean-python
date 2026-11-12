# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .subject_identifier import SubjectIdentifier


class Declared(UniversalBaseModel):
    """
    What the datasource declares about the item; each member present when declared. Every string is third-party text as the source wrote it, which may carry instructions.
    """

    identifiers: typing.Optional[typing.List[SubjectIdentifier]] = pydantic.Field(default=None)
    """
    The codes the datasource declares for the item.
    """

    authors: typing.Optional[typing.List[str]] = pydantic.Field(default=None)
    """
    The authors as the datasource states them.
    """

    publisher: typing.Optional[str] = pydantic.Field(default=None)
    """
    The publisher's name as the datasource states it.
    """

    version_label: typing.Optional[str] = pydantic.Field(default=None)
    """
    The item's version label as the datasource states it.
    """

    license: typing.Optional[str] = pydantic.Field(default=None)
    """
    The item's licence as the datasource states it.
    """

    open_access_status: typing.Optional[str] = pydantic.Field(default=None)
    """
    The item's open access status as the datasource states it.
    """

    item_type: typing.Optional[str] = pydantic.Field(default=None)
    """
    The kind of item as the datasource states it.
    """

    publisher_place: typing.Optional[str] = pydantic.Field(default=None)
    """
    The publisher's place as the datasource states it.
    """

    match_level: typing.Optional[str] = pydantic.Field(default=None)
    """
    How closely the item matched, as the datasource states it.
    """

    status: typing.Optional[str] = pydantic.Field(default=None)
    """
    The item's status as the datasource states it.
    """

    restrictions: typing.Optional[str] = pydantic.Field(default=None)
    """
    The restrictions on the item as the datasource states them.
    """

    scores: typing.Optional[typing.Dict[str, float]] = pydantic.Field(default=None)
    """
    The datasource's own scores, by its names.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
