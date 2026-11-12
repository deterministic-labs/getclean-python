# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .wording_language_basis import WordingLanguageBasis
from .wording_origin import WordingOrigin


class Wording(UniversalBaseModel):
    """
    One version of the question sent to the sources.
    """

    index: int = pydantic.Field()
    """
    The wording's position, from 0.
    """

    text: str = pydantic.Field()
    """
    The wording as it ran.
    """

    language: str = pydantic.Field()
    """
    The wording's language, a BCP 47 tag.
    """

    language_basis: WordingLanguageBasis = pydantic.Field()
    """
    How the language was known: `declared` by you, or `detected`. A closed set.
    """

    origin: WordingOrigin = pydantic.Field()
    """
    Where the wording came from: `caller`, your `query`; `alternate`, one of your `alternate_queries`; `or_split`, one side of an OR in the question; `identifier`, an identifier's value; `engine_correction`, a correction getclean made. A closed set.
    """

    correction_kind: typing.Optional[str] = pydantic.Field(default=None)
    """
    What was corrected, `spelling`; an open set. Present with origin `engine_correction`.
    """

    result_counts: typing.Dict[str, int] = pydantic.Field()
    """
    How many results each source gave this wording, keyed by datasource id.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
