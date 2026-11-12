# Generated from the getclean API contract; do not edit.

import typing

from ..core.api_error import ApiError
from ..types.problem import Problem


class GoneError(ApiError):
    def __init__(self, body: Problem, headers: typing.Optional[typing.Dict[str, str]] = None):
        super().__init__(status_code=410, headers=headers, body=body)
