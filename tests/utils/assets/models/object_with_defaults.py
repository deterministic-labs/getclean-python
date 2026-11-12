# Part of the generated SDK of the getclean API; do not edit.

import typing_extensions


class ObjectWithDefaultsParams(typing_extensions.TypedDict):
    """
    Defines properties with default values and validation rules.
    """

    decimal: typing_extensions.NotRequired[float]
    string: typing_extensions.NotRequired[str]
    required_string: str
