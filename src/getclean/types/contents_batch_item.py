# Generated from the getclean API contract; do not edit.

import datetime as dt
import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class ContentsBatchItem(UniversalBaseModel):
    """
    One fetch of a batch: its address, your label for it, and the few fields that are its own; every other field comes from the top of the request. The object is closed: a top-only field here is refused `misplaced`, an unknown one `unknown_field`.
    """

    url: str = pydantic.Field()
    """
    The address to fetch, a page or a document. Required. http or https, at most 2,048 characters, under the same address and domain rules as a fetch; a fault in the address or its domain skips this item alone, with its problem beside it, and the batch runs.
    """

    label: typing.Optional[str] = pydantic.Field(default=None)
    """
    Your label for this item, returned on its result so you can match answers to addresses; 1 to 64 of `a-z`, `0-9` and `-`, unique within the batch, a repeat refused `duplicate`. Default none.
    """

    highlights: typing.Optional[typing.List[str]] = pydantic.Field(default=None)
    """
    Words or questions to find in this page and mark where they stand, as on `fetch_contents`: 1 to 5 strings of 1 to 4,000 characters each. Default none.
    """

    baseline_fingerprint: typing.Optional[str] = pydantic.Field(default=None)
    """
    The fingerprint of a copy of this page you already hold, as a record returned it. When the page still matches it, the record is `unchanged` with no text, at the fetch's price. Default none.
    """

    as_of_date: typing.Optional[dt.date] = pydantic.Field(default=None)
    """
    This page's archive day, overriding the top's; a date not after today in UTC. Default the top's.
    """

    subject_country: typing.Optional[str] = pydantic.Field(default=None)
    """
    The country this page is read from, overriding the top's; one of `Limits.exits`. Default the top's.
    """

    subject_language: typing.Optional[str] = pydantic.Field(default=None)
    """
    The language to ask this site for, overriding the top's; a BCP 47 tag of 1 to 35 characters. Default the top's.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
