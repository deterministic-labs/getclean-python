# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class ModelStep(UniversalBaseModel):
    """
    One step a model, or a versioned recognizer, took in making the answer.
    """

    step: str = pydantic.Field()
    """
    Which step ran: `highlights`, the judged highlights; `json_schema`, the schema fill; `summary`, the summary; `recognition`, text read from a page with no text layer; `language_detection`, the languages chosen for that reading; `reranking`, the search's ranking; `discovery`, the search's choice of sources; `source_profile`, a publisher identified during the call. An open set.
    """

    version: str = pydantic.Field()
    """
    The step's version, so a result can be placed and compared.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
