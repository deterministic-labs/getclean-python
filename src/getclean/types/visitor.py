# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class Visitor(UniversalBaseModel):
    """
    From where the site was read: the country, the language asked for and the kind of network.
    """

    country: str = pydantic.Field()
    """
    The country the site was read from, ISO 3166-1 alpha-2.
    """

    language: str = pydantic.Field()
    """
    The language asked of the site, as the `Accept-Language` header sent.
    """

    network: str = pydantic.Field()
    """
    The kind of network the site was read from, an open set: `datacenter`, `residential`, `mobile`.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
