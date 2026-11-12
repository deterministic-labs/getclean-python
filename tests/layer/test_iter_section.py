"""iter_section: every page of a section in turn, from get_section, each asked with the token of the page before and
with the caller's own parameters, from the first page or from the token the caller gives, until the page that carries
no next_page_token."""

import typing

import pytest
from ._support import (
    CLIENTS,
    CONTENTS_ID,
    EXAMPLES,
    Answer,
    Body,
    Script,
    clock,
    drain,
    example,
    refusal,
    request_id,
    under_request_id,
)

from getclean.core.pydantic_utilities import parse_obj_as
from getclean.errors import BadRequestError
from getclean.types.section_contents import SectionContents

# Every test of this file runs with time stood in, so that none waits for real, even on a client that waits
# where it should not.
pytestmark = pytest.mark.usefixtures(clock.__name__)

SECTION_ID = EXAMPLES["get_section.fits"]["section"]["id"]
SECTION = f"/v1/contents/{CONTENTS_ID}/sections/{SECTION_ID}"


def page(n: int, next_page_token: typing.Optional[str]) -> Body:
    """The n-th page of the section: get_section's example under the request id of the page's own call. A page that is
    not the last carries the token of the page after it, an opaque string, and truncated true, since its text was cut
    and the token continues it."""
    body = under_request_id(example("get_section.fits"), request_id(f"Page{n}"))
    if next_page_token is not None:
        body.update(next_page_token=next_page_token, truncated=True)
    return body


THREE_PAGES = [page(1, "page-2"), page(2, "page-3"), page(3, None)]


async def pages(client: typing.Any, **parameters: typing.Any) -> typing.List[SectionContents]:
    """Every page iter_section yields for the example's section of the record, iterated as a caller iterates it."""
    yielded: typing.List[SectionContents] = []
    await drain(client.iter_section(CONTENTS_ID, SECTION_ID, **parameters), yielded)
    return yielded


@CLIENTS
async def test_three_pages_come_in_turn_each_asked_with_the_token_of_the_page_before(client_class: type) -> None:
    """Three pages are yielded in order, the first asked with no token, each later one with the token of the page
    before, and the third, which carries none, is the last."""
    script = Script([Answer("GET", SECTION, 200, body) for body in THREE_PAGES])

    yielded = await pages(script.client_for(client_class))

    assert yielded == [parse_obj_as(SectionContents, body) for body in THREE_PAGES], "the three pages, in turn"
    assert [r.url.params.get("page_token") for r in script.requests] == [None, "page-2", "page-3"], (
        "each page asked with the token of the page before"
    )
    assert script.unanswered == [] and script.unexpected == [], f"no request after the last page: {script.unexpected}"


@CLIENTS
async def test_every_page_is_asked_with_the_callers_own_parameters(client_class: type) -> None:
    """max_characters, scope, formats and block_kinds go on every page's request, the first and the later ones."""
    script = Script([Answer("GET", SECTION, 200, body) for body in THREE_PAGES])

    await pages(
        script.client_for(client_class),
        max_characters=5000,
        scope="whole_page",
        formats=["markdown", "html"],
        block_kinds=["text", "table"],
    )

    callers = [
        ("max_characters", "5000"),
        ("scope", "whole_page"),
        ("formats", "markdown"),
        ("formats", "html"),
        ("block_kinds", "text"),
        ("block_kinds", "table"),
    ]
    tokens: typing.List[typing.List[typing.Tuple[str, str]]] = [
        [],
        [("page_token", "page-2")],
        [("page_token", "page-3")],
    ]
    assert [sorted(r.url.params.multi_items()) for r in script.requests] == [sorted(callers + t) for t in tokens], (
        "the caller's parameters on every page, with each page's token"
    )
    assert script.unexpected == [], f"only the requests the pager calls for: {script.unexpected}"


@CLIENTS
async def test_iter_section_starts_at_the_page_token_the_caller_gives(client_class: type) -> None:
    """iter_section takes page_token as get_section does: the first request carries the token the caller holds, and the
    pages go on from there."""
    script = Script([Answer("GET", SECTION, 200, body) for body in THREE_PAGES[1:]])

    yielded = await pages(script.client_for(client_class), page_token="page-2")

    assert [r.url.params.get("page_token") for r in script.requests] == ["page-2", "page-3"], "from the token given"
    assert yielded == [parse_obj_as(SectionContents, body) for body in THREE_PAGES[1:]], "the pages from there on"
    assert script.unexpected == [], f"only the requests the pager calls for: {script.unexpected}"


@CLIENTS
async def test_a_section_of_one_page_is_one_request(client_class: type) -> None:
    """A section whose first page carries no next_page_token is that one page, after one request."""
    only = page(1, None)
    script = Script([Answer("GET", SECTION, 200, only)])

    yielded = await pages(script.client_for(client_class))

    assert yielded == [parse_obj_as(SectionContents, only)], "the one page"
    assert len(script.requests) == 1 and script.unexpected == [], "one request"


@CLIENTS
async def test_a_later_page_refused_page_token_invalid_raises_the_typed_error(client_class: type) -> None:
    """A later page refused 400 page-token-invalid raises the typed error of that status, after the pages before it were
    yielded."""
    refused = refusal("GET", SECTION, "page-token-invalid", 400)
    script = Script([Answer("GET", SECTION, 200, THREE_PAGES[0]), refused])
    yielded: typing.List[SectionContents] = []

    with pytest.raises(BadRequestError) as raised:
        await drain(script.client_for(client_class).iter_section(CONTENTS_ID, SECTION_ID), yielded)

    assert yielded == [parse_obj_as(SectionContents, THREE_PAGES[0])], "the first page came before the error"
    assert raised.value.body.type == refused.body["type"], "the refusal of the later page is raised"
    assert len(script.requests) == 2 and script.unexpected == [], "no request after the refusal"
