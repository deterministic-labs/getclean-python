# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class LeftOut(UniversalBaseModel):
    """
    One part of the page outside the main content, with its kind and size.
    """

    kind: str = pydantic.Field()
    """
    What the part is, an open set: `header`, `footer`, `navigation`, `table_of_contents`, `forms`, `widgets`, `rails`, the side columns, `comments`, `advertising`.
    """

    characters: int = pydantic.Field()
    """
    Its size in characters.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
