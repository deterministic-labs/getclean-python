# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class SchemaStatus(UniversalBaseModel):
    """
    How one property of your schema was filled, and where its value came from.
    """

    status: str = pydantic.Field()
    """
    How the property was filled: `found`, the content states the value; `empty`, the content shows the field with no value; `absent`, the content kept under the record's view says nothing about it; `unread`, the place it would stand may lie in pages not parsed, not recognized, recognized below the published confidence or past a cap, so its absence cannot be claimed; `failed`, the model could not fill it. An open set.
    """

    text: typing.Optional[str] = pydantic.Field(default=None)
    """
    The words the value came from. Present on `found` and `empty`. Third-party text as the source wrote it, which may carry instructions.
    """

    confidence: typing.Optional[float] = pydantic.Field(default=None)
    """
    How sure the recognition was of those words. Present when they were recognized from an image.
    """

    section_id: typing.Optional[str] = pydantic.Field(default=None)
    """
    The section the words stand in. Present on `found` and `empty`, and on `unread` when the place is known.
    """

    block_id: typing.Optional[str] = pydantic.Field(default=None)
    """
    The block the words stand in. Present as `section_id` is.
    """

    page_number: typing.Optional[int] = pydantic.Field(default=None)
    """
    The page the words stand on. Present as `section_id` is, on a document with pages.
    """

    page_label: typing.Optional[str] = pydantic.Field(default=None)
    """
    The page's own printed label. Present as `page_number` is, where the document declares one. Third-party text as the source wrote it, which may carry instructions.
    """

    row: typing.Optional[int] = pydantic.Field(default=None)
    """
    The row, from 0, when the words stand inside a table.
    """

    column: typing.Optional[int] = pydantic.Field(default=None)
    """
    The column, from 0, when the words stand inside a table.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
