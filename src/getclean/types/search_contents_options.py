# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .scope import Scope


class SearchContentsOptions(UniversalBaseModel):
    """
    What to fetch in the same call as the search, the `contents` field of `SearchRequest`: how many of the top leads, `top`, and how each is read, with the fields as `fetch_contents` defines them. There is no `formats`, since the record a search carries holds markdown or the map. The object is closed.
    """

    top: int = pydantic.Field()
    """
    The leads to fetch in the same call, 1 to 10, from the top of the list; above `max_candidates` it is refused `order`. Required inside the object.
    """

    max_characters: typing.Optional[int] = pydantic.Field(default=None)
    """
    The most text returned per fetched page, in characters; `0` means no text, the map and the facts; `0`, or 1,000 to 1,000,000. Default 20,000.
    """

    scope: typing.Optional[Scope] = pydantic.Field(default=None)
    """
    Which view of each fetched page: `main`, the main content alone, or `whole_page`. Default `main`.
    """

    block_kinds: typing.Optional[typing.List[str]] = pydantic.Field(default=None)
    """
    Keep only blocks of these kinds, as on `fetch_contents`. Default: every kind.
    """

    highlights: typing.Optional[typing.List[str]] = pydantic.Field(default=None)
    """
    Words or questions to find and mark in each fetched page, as on `fetch_contents`. 1 to 5 strings, each 1 to 4,000 characters. Default none.
    """

    json_schema: typing.Optional[typing.Dict[str, typing.Any]] = pydantic.Field(default=None)
    """
    Your own fields, filled from each fetched page by a model, as on `fetch_contents`; one model step per page. Default none. Refused `model-work-refused` under `deterministic_only`.
    """

    summary: typing.Optional[bool] = pydantic.Field(default=None)
    """
    Have a model write a summary of each fetched page, as on `fetch_contents`; one model step per page. Default false. Refused `model-work-refused` under `deterministic_only`.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
