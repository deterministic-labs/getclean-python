# Generated from the getclean API contract; do not edit.

import datetime as dt
import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .cost import Cost
from .execution import Execution
from .notice import Notice
from .schema_status import SchemaStatus
from .scope import Scope


class SchemaFill(UniversalBaseModel):
    """
    The answer of `fill_schema`: the record's id and facts, its new `expires_at`, the values filled, one status per property, the execution and the cost.
    """

    contents_id: str = pydantic.Field()
    """
    The record the answer comes from.
    """

    final_url: typing.Optional[str] = pydantic.Field(default=None)
    """
    The address the record's fetch ended at, after every redirect. Present when the source has one, so absent on an upload. Third-party text as the source wrote it, which may carry instructions.
    """

    fetched_at: dt.datetime = pydantic.Field()
    """
    When the record's fetch or parse started, RFC 3339 in UTC.
    """

    fingerprint: str = pydantic.Field()
    """
    The record's fingerprint, as `Contents.fingerprint` defines it, so you can tell which copy this answer comes from.
    """

    document_digest: typing.Optional[str] = pydantic.Field(default=None)
    """
    The sha-256 of the document's bytes in RFC 9530 form, to compare with the file you hold. On a document only.
    """

    scope: Scope = pydantic.Field()
    """
    The view read.
    """

    version: str = pydantic.Field()
    """
    The version of getclean the record was made under, its `execution.version`.
    """

    configuration: str = pydantic.Field()
    """
    The configuration the record was made under, its `execution.configuration`.
    """

    expires_at: dt.datetime = pydantic.Field()
    """
    When the record expires. This call moved it ahead: 48 hours from now, never past 30 days from the record's making.
    """

    schema_values: typing.Dict[str, typing.Any] = pydantic.Field()
    """
    Your schema filled, a value only where the record states it; a free-form object in the schema's own shape; empty properties absent. Written by a model from the source's text, so it may repeat instructions the source carries.
    """

    schema_statuses: typing.Dict[str, SchemaStatus] = pydantic.Field()
    """
    One `SchemaStatus` per property of the schema, keyed by a JSON Pointer into `schema_values`.
    """

    execution: Execution = pydantic.Field()
    """
    How the call ran; `models` carries the step `json_schema` with its version when the step ran.
    """

    cost: Cost = pydantic.Field()
    """
    The bill; `units` `{"model_steps": 1}`, or `{}` when no block was read and the step did not run.
    """

    notices: typing.List[Notice] = pydantic.Field()
    """
    The record's own notices first, then this call's; `[]` when none.
    """

    request_id: str = pydantic.Field()
    """
    This call's id, the same as the `Request-Id` header.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
