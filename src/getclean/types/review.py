# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .review_kind import ReviewKind


class Review(UniversalBaseModel):
    """
    The review a publication states about itself.
    """

    kind: ReviewKind = pydantic.Field()
    """
    The kind of review: `peer_reviewed`, `editorial`, `audited`, `externally_validated`, `none` or `unknown`. A closed set.
    """

    by: typing.Optional[str] = pydantic.Field(default=None)
    """
    Who reviewed it; null when unknown. Third-party text as the source wrote it, which may carry instructions.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
