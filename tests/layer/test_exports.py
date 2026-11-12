"""What a caller imports from the package root, and JobCanceled, the one error of the SDK's own that a call raises."""

import typing

import pytest
from ._support import (
    CLIENTS,
    JOB_ID,
    Script,
    accepted,
    canceled_without_record,
    clock,
    limits_read,
    polled,
    queued,
    settle,
)

import getclean
import getclean.client
import getclean.core.api_error
import getclean.core.configuration_error
import getclean.errors.job_canceled
from getclean.base_client import AsyncBaseGetClean, BaseGetClean
from getclean.client import DocumentInput
from getclean.core.pydantic_utilities import parse_obj_as
from getclean.types.job import Job

# Every test of this file runs with time stood in, so that none waits for real, even on a client that waits
# where it should not.
pytestmark = pytest.mark.usefixtures(clock.__name__)


def test_the_root_exports_the_two_clients_and_the_errors_a_caller_catches() -> None:
    """from getclean import GetClean, AsyncGetClean, ApiError, ConfigurationError and JobCanceled gives the two clients
    and the three error classes, each the one class of its name, and the two clients are the client's own, built on the
    base clients."""
    from getclean import ApiError, AsyncGetClean, ConfigurationError, GetClean, JobCanceled

    assert GetClean is getclean.client.GetClean and GetClean is not BaseGetClean, "GetClean is the client's own"
    assert issubclass(GetClean, BaseGetClean), "GetClean is built on the base client"
    assert AsyncGetClean is getclean.client.AsyncGetClean and AsyncGetClean is not AsyncBaseGetClean, (
        "AsyncGetClean is the client's own"
    )
    assert issubclass(AsyncGetClean, AsyncBaseGetClean), "AsyncGetClean is built on the async base client"
    assert ApiError is getclean.core.api_error.ApiError, "one ApiError class"
    assert ConfigurationError is getclean.core.configuration_error.ConfigurationError, "one ConfigurationError class"
    assert JobCanceled is getclean.errors.job_canceled.JobCanceled, "one JobCanceled class"
    assert {"GetClean", "AsyncGetClean", "ApiError", "ConfigurationError", "JobCanceled"} <= set(getclean.__all__), (
        "the root lists the two clients and the three errors among its exports"
    )


def test_job_canceled_carries_the_job_and_its_message_names_the_job() -> None:
    """JobCanceled carries the canceled job and its message names the job's id; it is an Exception of the SDK's own,
    no HTTP error, since a cancel is no refusal."""
    canceled = parse_obj_as(Job, canceled_without_record())

    error = getclean.JobCanceled(canceled)

    assert error.job is canceled, "JobCanceled carries the job"
    assert JOB_ID in str(error), "its message names the job"
    assert isinstance(error, Exception) and not isinstance(error, getclean.ApiError), "an Exception, no HTTP error"


@CLIENTS
async def test_the_job_canceled_a_call_raises_is_one_class_on_both_import_paths(client_class: type) -> None:
    """The JobCanceled the wait raises is caught under either import path, the package root or its own module."""
    script = Script([limits_read(), accepted(queued()), polled(canceled_without_record())])

    with pytest.raises(getclean.errors.job_canceled.JobCanceled) as raised:
        await settle(script.client_for(client_class).upload_contents(document=b"%PDF-1.7", wait=True))

    assert isinstance(raised.value, getclean.JobCanceled), "caught under the root's name too"
    assert type(raised.value) is getclean.errors.job_canceled.JobCanceled, "one class, not a subclass"
    assert script.unexpected == [], f"only the requests the wait calls for: {script.unexpected}"


def a_callers_upload(document: DocumentInput) -> None:
    """An upload of a caller's own, annotated with DocumentInput, in a module that imports nothing else of the client
    module and nothing of os."""


def test_the_type_of_the_uploads_document_resolves_in_a_callers_own_module() -> None:
    """DocumentInput, the type of the upload's document, a path, bytes, a stream or a tuple, is exported by the client
    module, and resolves in a caller's own module as it is: read back from a caller's annotation, in a namespace that
    holds DocumentInput and nothing else, it is the type upload_contents takes."""
    resolved = typing.get_type_hints(a_callers_upload, globalns={"DocumentInput": DocumentInput}, localns={})

    assert "DocumentInput" in getclean.client.__all__, "the client module exports DocumentInput"
    for client_class in (getclean.GetClean, getclean.AsyncGetClean):
        takes = typing.get_type_hints(client_class.upload_contents)["document"]
        a_callers = resolved["document"]
        assert takes == typing.Optional[a_callers], (
            f"{client_class.__name__}.upload_contents takes the DocumentInput a caller reads back"
        )


def test_the_root_exports_the_type_of_the_uploads_document() -> None:
    """from getclean import DocumentInput gives the very type the client module exports, as the root gives the clients
    and the errors."""
    assert getattr(getclean, "DocumentInput", None) is DocumentInput, "the root exports DocumentInput"
    assert "DocumentInput" in getclean.__all__, "the root lists DocumentInput among its exports"
