# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .contents_compact import ContentsCompact
from .notice import Notice


class ContentsPage(UniversalBaseModel):
    """
    One page of the records the account keeps, newest first, the answer of `list_contents`. Each record is compact: its id, outcome, source and dates, with no text, no map, no model work and no cost.
    """

    contents: typing.List[ContentsCompact] = pydantic.Field()
    """
    The records of this page, each a `ContentsCompact` without `cost`; `[]` when none matches.
    """

    next_page_token: typing.Optional[str] = pydantic.Field(default=None)
    """
    The token for the next page; pass it as `page_token`. Present while more remains, and a page that carries it always has at least one record.
    """

    notices: typing.List[Notice] = pydantic.Field()
    """
    This call's notices, `page_size_lowered` and `version_retiring`; `[]` when there is none.
    """

    request_id: str = pydantic.Field()
    """
    This call's id, the same as the `Request-Id` header.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
