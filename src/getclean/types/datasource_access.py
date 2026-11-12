# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .money import Money


class DatasourceAccess(UniversalBaseModel):
    """
    How a datasource is reached.
    """

    kind: str = pydantic.Field()
    """
    How the source is reached: `open`, no login; `registered`, a login the account owner registers; `paid`, a fee per query. An open set.
    """

    fee: typing.Optional[Money] = pydantic.Field(default=None)
    """
    The fee per query. Present when the source charges one.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
