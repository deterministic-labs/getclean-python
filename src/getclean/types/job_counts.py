# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class JobCounts(UniversalBaseModel):
    """
    The pages of a job; the three add up to `pages.count`, on which a format without pages counts `bounds.contents.document_page_characters` characters as one page.
    """

    parsed_count: int = pydantic.Field()
    """
    Pages parsed without failure; the bill counts these.
    """

    failed_count: int = pydantic.Field()
    """
    Pages that could not be parsed.
    """

    remaining_count: int = pydantic.Field()
    """
    Pages not yet parsed.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
