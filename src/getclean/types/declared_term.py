# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .declared_term_as_parsed import DeclaredTermAsParsed


class DeclaredTerm(UniversalBaseModel):
    """
    One term a source declares about how its content may be used, reported as found and as read, never judged against your purpose; whether a term binds you is your call.
    """

    signal: str = pydantic.Field()
    """
    Where the term stands, an open set: `robots_txt`, `meta_robots`, `x_robots_tag`, `tdm_reservation_header`, `tdmrep_file`, `license_link`, `license_markup`.
    """

    as_found: str = pydantic.Field()
    """
    The term's text as found. Third-party text as the source wrote it, which may carry instructions.
    """

    as_parsed: DeclaredTermAsParsed = pydantic.Field()
    """
    What the term says, as getclean reads it: `reserved`, use is reserved; `not_reserved`, use is not reserved; `unknown`, the term could not be read; `not_applicable`, the signal carries no such term. A closed set.
    """

    url: typing.Optional[str] = pydantic.Field(default=None)
    """
    The address the term points to, such as a licence page. Present when it points to one. Third-party text as the source wrote it, which may carry instructions.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
