# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .model_step import ModelStep
from .time_stamp import TimeStamp


class Execution(UniversalBaseModel):
    """
    How the answer was made: the version, its configuration, the model steps that ran and the time it took.
    """

    version: str = pydantic.Field()
    """
    getclean's version, the value `pinned_version` pins and `Limits.current_version` names.
    """

    configuration: str = pydantic.Field()
    """
    The read configuration as one published string, fixed with the version by `pinned_version`. Under one version and one configuration the same page, or the same bytes, give the same text and the same ids.
    """

    models: typing.List[ModelStep] = pydantic.Field()
    """
    Every model step, and every versioned recognition step, that ran in making this answer, each with its version; `[]` when none ran.
    """

    elapsed_seconds: float = pydantic.Field()
    """
    The seconds the work took.
    """

    time_stamp: typing.Optional[TimeStamp] = pydantic.Field(default=None)
    """
    A trusted time over the record's fingerprint and the screenshot's digest. Not sent in this version.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
