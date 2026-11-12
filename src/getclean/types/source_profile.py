# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .review import Review
from .source_profile_independence import SourceProfileIndependence
from .source_profile_role import SourceProfileRole


class SourceProfile(UniversalBaseModel):
    """
    Who publishes the source, as getclean identifies it from the site's own declarations and from public registries: no score, no tier, no verdict. Identifying a publisher costs nothing extra; when getclean identifies one during the call, the step `source_profile` is listed in `execution.models`. Under `deterministic_only` only what is already known answers. A kind that cannot be read from the declarations is `unknown`, never a guess.
    """

    kind: str = pydantic.Field()
    """
    The kind of publisher; an open set with these published values, by sector. Public: `state`, `court`, `regulator`, `statistics_office`, `intergovernmental`, `standards_body`. Knowledge: `academic`, `scholarly_publisher`, `archive`, `reference`. Media: `press`, `information_provider`. Economy: `company`, `professional_practice`, `trade_body`, `marketplace`. Society: `civil_society`, `political`, `religious`, `education`, `healthcare`, `cultural`. Individual: `individual`, `community`. And `unknown`.
    """

    role: SourceProfileRole = pydantic.Field()
    """
    What the item is as a source: `primary`, `secondary` or `tertiary` in the usual sense of research, else `unknown`. Read from the item's declared type first, then from the publisher's kind. A closed set.
    """

    independence: SourceProfileIndependence = pydantic.Field()
    """
    Whether the publisher is the subject speaking about itself, `self`, or independent of it, `independent`, known through the subject's identifiers; else `unknown`. A closed set.
    """

    review: Review = pydantic.Field()
    """
    Who reviewed the publication, from the venue's stated process or a named validator.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
