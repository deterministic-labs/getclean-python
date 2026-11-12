"""The upload's document as a path, bytes or a readable stream. A path, a str or an os.PathLike, always means the file
at that path, sent under its base name; bytes and the tuple forms go as they are; a stream is read into memory once,
before the first attempt, so every attempt sends the same bytes under the same key."""

import os
import pathlib
import typing

import pytest
from ._support import (
    CLIENTS,
    UPLOAD,
    UPLOAD_CALL,
    Script,
    clock,
    limits_read,
    settle,
    the_document,
)

# Every test of this file runs with time stood in, so that none waits for real, even on a client that waits
# where it should not.
pytestmark = pytest.mark.usefixtures(clock.__name__)

MINUTES = b"%PDF-1.7 the ten pages of the minutes"
"""The bytes of the file the tests upload, standing for the minutes.pdf of the upload's example."""


def a_file(tmp_path: pathlib.Path) -> pathlib.Path:
    path = tmp_path / "minutes.pdf"
    path.write_bytes(MINUTES)
    return path


def answered_once() -> Script:
    return Script([limits_read(), UPLOAD_CALL.answered()])


def in_flight_then_answered() -> Script:
    """The upload refused once as in flight, asking a wait of 1 second, then answered."""
    return Script([limits_read(), UPLOAD_CALL.refused("idempotency-key-in-flight", 409, 1), UPLOAD_CALL.answered()])


@CLIENTS
@pytest.mark.parametrize("form", [str, pathlib.Path], ids=["str", "PathLike"])
async def test_a_path_sends_the_files_bytes_under_its_base_name(
    tmp_path: pathlib.Path, client_class: type, form: typing.Callable[[pathlib.Path], typing.Any]
) -> None:
    """A path, as a str or an os.PathLike, sends the bytes of the file at that path under the file's base name."""
    script = answered_once()

    await settle(script.client_for(client_class).upload_contents(document=form(a_file(tmp_path))))

    part = the_document(script.sent("POST", UPLOAD)[0])
    assert (part.filename, part.content) == ("minutes.pdf", MINUTES), "a path sends the file's bytes under its name"
    assert script.unexpected == [], f"only the requests the upload calls for: {script.unexpected}"


@CLIENTS
async def test_a_path_with_no_file_raises_file_not_found_before_any_request(
    tmp_path: pathlib.Path, client_class: type
) -> None:
    """A path where no file is raises FileNotFoundError before any request leaves, since a str always means a path."""
    script = Script([])

    with pytest.raises(FileNotFoundError):
        await settle(script.client_for(client_class).upload_contents(document=str(tmp_path / "missing.pdf")))

    assert script.requests == [], "no request leaves, not even the limits read"


@CLIENTS
async def test_bytes_go_as_the_base_client_sends_them(client_class: type) -> None:
    """Bytes go as the very part the base client sends for the same bytes: the client adds nothing to them."""
    script = Script([limits_read(), UPLOAD_CALL.answered(), UPLOAD_CALL.answered()])

    await settle(script.client_for(client_class).upload_contents(document=MINUTES))
    await settle(script.base_client_for(client_class).upload_contents(document=MINUTES))

    ours, the_bases = (the_document(request) for request in script.sent("POST", UPLOAD))
    assert ours == the_bases, f"bytes go as the base client sends them: {ours} against {the_bases}"
    assert ours.content == MINUTES, "the part carries the bytes given"
    assert script.unexpected == [], f"only the requests the uploads call for: {script.unexpected}"


@CLIENTS
async def test_an_open_file_goes_as_the_base_client_sends_it(tmp_path: pathlib.Path, client_class: type) -> None:
    """An open binary file goes as the very part the base client sends for the same file: read whole, under the same
    name, type and bytes."""
    script = Script([limits_read(), UPLOAD_CALL.answered(), UPLOAD_CALL.answered()])

    with a_file(tmp_path).open("rb") as stream:
        await settle(script.client_for(client_class).upload_contents(document=stream))
    with a_file(tmp_path).open("rb") as stream:
        await settle(script.base_client_for(client_class).upload_contents(document=stream))

    ours, the_bases = (the_document(request) for request in script.sent("POST", UPLOAD))
    assert ours == the_bases, f"an open file goes as the base client sends it: {ours} against {the_bases}"
    assert ours.content == MINUTES, "the part carries the file's bytes"
    assert script.unexpected == [], f"only the requests the uploads call for: {script.unexpected}"


@CLIENTS
async def test_a_tuple_passes_through_with_its_name_and_type(client_class: type) -> None:
    """A tuple of name, bytes and media type goes as it is: its name, its type and its bytes."""
    script = answered_once()

    await settle(script.client_for(client_class).upload_contents(document=("minutes.pdf", MINUTES, "application/pdf")))

    part = the_document(script.sent("POST", UPLOAD)[0])
    assert (part.filename, part.content_type, part.content) == ("minutes.pdf", "application/pdf", MINUTES), (
        "a tuple goes with its own name, type and bytes"
    )
    assert script.unexpected == [], f"only the requests the upload calls for: {script.unexpected}"


@CLIENTS
@pytest.mark.parametrize("wait", [False, True], ids=["wait=False", "wait=True"])
async def test_a_path_means_the_file_whether_or_not_wait_is_set(
    tmp_path: pathlib.Path, client_class: type, wait: bool
) -> None:
    """A str path means the file at that path with wait unset or set alike."""
    script = answered_once()

    await settle(script.client_for(client_class).upload_contents(document=str(a_file(tmp_path)), wait=wait))

    part = the_document(script.sent("POST", UPLOAD)[0])
    assert (part.filename, part.content) == ("minutes.pdf", MINUTES), "a path means the file, whatever wait says"
    assert script.unexpected == [], f"only the requests the upload calls for: {script.unexpected}"


@CLIENTS
@pytest.mark.parametrize("form", ["path", "bytes", "open file"])
async def test_the_retry_of_an_in_flight_409_sends_the_same_document_again(
    tmp_path: pathlib.Path, client_class: type, form: str
) -> None:
    """The retry of an in-flight 409 sends the whole document again, in each of its forms, so the server compares the
    same body under the same key."""
    script = in_flight_then_answered()
    path = a_file(tmp_path)
    client = script.client_for(client_class)

    if form == "open file":
        with path.open("rb") as stream:
            await settle(client.upload_contents(document=stream))
    else:
        await settle(client.upload_contents(document=str(path) if form == "path" else MINUTES))

    contents = [the_document(request).content for request in script.sent("POST", UPLOAD)]
    assert contents == [MINUTES, MINUTES], "the same whole document on both attempts"
    assert script.unexpected == [], f"only the requests the upload calls for: {script.unexpected}"


@CLIENTS
async def test_a_stream_read_only_once_is_read_into_memory_before_the_first_attempt(client_class: type) -> None:
    """A stream that cannot be read a second time, here the read end of a pipe, is read into memory once before the
    first attempt, so the retry of an in-flight 409 sends the same bytes under the same key."""
    script = in_flight_then_answered()
    read_end, write_end = os.pipe()
    os.write(write_end, MINUTES)
    os.close(write_end)

    with os.fdopen(read_end, "rb") as stream:
        await settle(script.client_for(client_class).upload_contents(document=stream))

    attempts = script.sent("POST", UPLOAD)
    assert [the_document(request).content for request in attempts] == [MINUTES, MINUTES], "the same bytes twice"
    assert len({request.headers["Idempotency-Key"] for request in attempts}) == 1, "under one key"
    assert script.unexpected == [], f"only the requests the upload calls for: {script.unexpected}"
