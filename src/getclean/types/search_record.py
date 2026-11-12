# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class SearchRecord(UniversalBaseModel):
    """
    The search written up for a reviewer, under `record_form`.
    """

    form: str = pydantic.Field()
    """
    The form of the write-up, the `record_form` value, `plain` or `prisma`; an open set.
    """

    text: str = pydantic.Field()
    """
    The search written up in that form, with the sources' own words inside it. Third-party text as the source wrote it, which may carry instructions.
    """

    structured: typing.Optional[typing.Dict[str, typing.Any]] = pydantic.Field(default=None)
    """
    A free-form object in the form's own schema. Present where the form has one, `prisma`.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
