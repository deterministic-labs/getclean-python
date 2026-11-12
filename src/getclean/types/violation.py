# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .bound import Bound
from .violation_place import ViolationPlace


class Violation(UniversalBaseModel):
    """
    One fault of a request, with where it is.
    """

    kind: str = pydantic.Field()
    """
    What kind of fault; an open set with these published values. `bound`, a length, count, range or size was passed; `not_allowed`, a value outside the published set; `dependent`, a field that needs another field; `exclusive`, two fields that exclude each other; `order`, two values in the wrong order; `duplicate`, a repeated value; `misplaced`, a known field at the wrong level of a batch; `unknown_field`, a field this operation does not take; `syntax`, a value of the wrong type or form; `required`, a required field missing.
    """

    place: ViolationPlace = pydantic.Field()
    """
    Where the fault is: `body`, `form`, `query`, `path` or `header`. A closed set.
    """

    pointer: typing.Optional[str] = pydantic.Field(default=None)
    """
    A JSON Pointer to the value. Present when the place is `body`; on a `form`, present when the fault is inside a JSON part, where it locates the value inside the part, or among a list field's repeated parts, where it names the index, `/1`.
    """

    field: str = pydantic.Field()
    """
    The field, parameter or header name. A field inside a batch item is named by its own name, the item standing in `pointer`; a fault in a map's key or value, `metadata`'s, is named by the map, the key standing in `pointer`.
    """

    message: str = pydantic.Field()
    """
    One sentence on what is wrong with the value.
    """

    allowed_values: typing.Optional[typing.List[str]] = pydantic.Field(default=None)
    """
    The values the field may take. Present when they apply.
    """

    bounds: typing.Optional[Bound] = pydantic.Field(default=None)
    """
    The range the field may take. Present when it applies.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
