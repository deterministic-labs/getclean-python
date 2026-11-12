# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class LanguageVersion(UniversalBaseModel):
    """
    One of the page's own language versions, as the page declares them.
    """

    url: str = pydantic.Field()
    """
    The version's address. Third-party text as the source wrote it, which may carry instructions.
    """

    language: str = pydantic.Field()
    """
    The version's language, a BCP 47 tag.
    """

    authoritative: typing.Optional[bool] = pydantic.Field(default=None)
    """
    Whether this version binds. Present only when the page declares, in a form getclean reads, which versions bind: true on a binding version and false on the others, and true on every version where the source declares them equally authentic. Absent when nothing is declared.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
