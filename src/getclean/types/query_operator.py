# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class QueryOperator(UniversalBaseModel):
    """
    One operator read from the question.
    """

    name: str = pydantic.Field()
    """
    Which operator: `phrase`, `exclusion`, `or`, `site`, `filetype`, `intitle`, `inurl`, `before`, `after` or `wildcard`; an open set.
    """

    value: str = pydantic.Field()
    """
    The operand as written.
    """

    field: typing.Optional[str] = pydantic.Field(default=None)
    """
    The request field the operator was read into, `allowed_domains` for `site:`, `media_types` for `filetype:`, `published_from` and `published_until` for `after:` and `before:`. Present when there is one.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
