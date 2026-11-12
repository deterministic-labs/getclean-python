# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class Origin(UniversalBaseModel):
    """
    One other site the page reached while it was read.
    """

    origin: str = pydantic.Field()
    """
    The site, as scheme and host. Third-party text as the source wrote it, which may carry instructions.
    """

    kind: str = pydantic.Field()
    """
    How it was reached, an open set: `form_action`, a form posts to it; `script`, a script was loaded from it; `frame`, a frame came from it; `fetch`, the page fetched data from it; `other`.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
