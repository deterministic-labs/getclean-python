"""The repeat filter of list_jobs and list_contents, the two lists that grow while they page: an item whose id was
already seen is dropped, a page left with nothing new is passed over, and each page keeps its own answer."""

import typing

import pytest
from ._support import (
    CLIENTS,
    Answer,
    Body,
    Script,
    clock,
    example,
    items_of,
    pages_of,
    request_id,
    settle,
    under_request_id,
)

from getclean.core.pydantic_utilities import parse_obj_as
from getclean.types.contents_page import ContentsPage
from getclean.types.job_page import JobPage

# Every test of this file runs with time stood in, so that none waits for real, even on a client that waits
# where it should not.
pytestmark = pytest.mark.usefixtures(clock.__name__)


class Listing(typing.NamedTuple):
    """A list that grows while it pages: its method, its path, the member holding its items, the prefix of an item's
    id, the type of its page, and the name of the API's example of its first page."""

    method: str
    path: str
    member: str
    prefix: str
    page_type: type
    first_page: str


LISTINGS = [
    Listing("list_jobs", "/v1/jobs", "jobs", "job", JobPage, "list_jobs.first-page"),
    Listing("list_contents", "/v1/contents", "contents", "cnt", ContentsPage, "list_contents.first-page"),
]
BOTH_LISTS = pytest.mark.parametrize("listing", LISTINGS, ids=[listing.method for listing in LISTINGS])

PAGE_SIZE = 500
"""A page_size above the most a page holds, 200, which the server lowers with the notice page_size_lowered on every
page, so each page carries a notice of its own."""

PAGE_SIZE_LOWERED = {
    "code": "page_size_lowered",
    "message": "page_size was above the maximum, 200, and was lowered to it.",
    "field": "page_size",
}


def item_id(listing: Listing, label: str) -> str:
    """An item id of the contract's form, the list's prefix, an underscore and 22 letters or digits."""
    return f"{listing.prefix}_{label.ljust(22, 'x')}"


def page(listing: Listing, n: int, labels: typing.Sequence[str], next_page_token: typing.Optional[str]) -> Answer:
    """The n-th page of the list: the list's example under the request id of the page's own call, which a job on the
    page carries too, since a job's request_id is the call it came back in; its one item copied under each id; the
    notice page_size_lowered; and the token of the page after it, an opaque string, or none on the last."""
    body: Body = under_request_id(example(listing.first_page), request_id(f"Page{n}"))
    item = body[listing.member][0]
    body[listing.member] = [dict(item, id=item_id(listing, label)) for label in labels]
    body["notices"] = [dict(PAGE_SIZE_LOWERED)]
    if next_page_token is not None:
        body["next_page_token"] = next_page_token
    return Answer("GET", listing.path, 200, body)


async def ids_listed(client: typing.Any, listing: Listing) -> typing.List[str]:
    pager = await settle(getattr(client, listing.method)(page_size=PAGE_SIZE))
    return [item.id for item in await items_of(pager)]


@CLIENTS
@BOTH_LISTS
async def test_an_id_on_two_pages_is_yielded_once(client_class: type, listing: Listing) -> None:
    """An item whose id came on an earlier page is not yielded again, page after page: b of the first page is dropped
    from the second, and c of the second from the third."""
    script = Script(
        [page(listing, 1, ["a", "b"], "t2"), page(listing, 2, ["b", "c"], "t3"), page(listing, 3, ["c", "d"], None)]
    )

    listed = await ids_listed(script.client_for(client_class), listing)

    assert listed == [item_id(listing, label) for label in ["a", "b", "c", "d"]], "an item already seen is dropped"
    assert script.unexpected == [], f"only the requests the pager calls for: {script.unexpected}"


@CLIENTS
@BOTH_LISTS
async def test_a_page_of_repeats_between_two_pages_is_passed_over(client_class: type, listing: Listing) -> None:
    """A page holding only repeats, between two pages with new items, is passed over: the caller sees two pages, each
    with its own answer, and the next page is still asked with the token of the page before."""
    answers = [page(listing, 1, ["a", "b"], "t2"), page(listing, 2, ["b"], "t3"), page(listing, 3, ["c"], None)]
    script = Script(answers)
    pager = await settle(getattr(script.client_for(client_class), listing.method)(page_size=PAGE_SIZE))

    seen = await pages_of(pager)

    assert [[item.id for item in p.items] for p in seen] == [
        [item_id(listing, "a"), item_id(listing, "b")],
        [item_id(listing, "c")],
    ], "two pages, the page of repeats passed over"
    assert [p.response for p in seen] == [parse_obj_as(listing.page_type, answers[n].body) for n in (0, 2)], (
        "each page shown keeps its own answer"
    )
    assert [r.url.params.get("page_token") for r in script.requests] == [None, "t2", "t3"], (
        "each page asked with the token of the page before"
    )
    assert script.unexpected == [], f"only the requests the pager calls for: {script.unexpected}"


@CLIENTS
@BOTH_LISTS
async def test_a_last_page_of_repeats_ends_the_iteration(client_class: type, listing: Listing) -> None:
    """A last page that holds only repeats ends the iteration with no error."""
    script = Script([page(listing, 1, ["a", "b"], "t2"), page(listing, 2, ["a", "b"], None)])

    listed = await ids_listed(script.client_for(client_class), listing)

    assert listed == [item_id(listing, "a"), item_id(listing, "b")], "the repeats of the last page dropped"
    assert len(script.requests) == 2 and script.unexpected == [], "the iteration ends at the last page"


@CLIENTS
@BOTH_LISTS
async def test_each_page_holds_its_own_answer(client_class: type, listing: Listing) -> None:
    """Each page's own members, its notices and its request id among them, are read from the page the pager holds, and
    are that page's answer."""
    answers = [page(listing, 1, ["a"], "t2"), page(listing, 2, ["b"], None)]
    script = Script(answers)
    pager = await settle(getattr(script.client_for(client_class), listing.method)(page_size=PAGE_SIZE))

    seen = await pages_of(pager)

    assert [p.response.request_id for p in seen] == [request_id("Page1"), request_id("Page2")], (
        "each page's own request id"
    )
    assert [[notice.code for notice in p.response.notices] for p in seen] == [["page_size_lowered"]] * 2, (
        "each page's own notices"
    )
    assert script.unexpected == [], f"only the requests the pager calls for: {script.unexpected}"


@CLIENTS
@BOTH_LISTS
async def test_a_pager_built_and_not_iterated_asks_for_the_first_page_alone(
    client_class: type, listing: Listing
) -> None:
    """A pager that is built and not iterated has asked for its first page and nothing more: a later page is read only
    when it is asked for."""
    script = Script([page(listing, 1, ["a"], "t2")])

    await settle(getattr(script.client_for(client_class), listing.method)(page_size=PAGE_SIZE))

    assert len(script.requests) == 1, "the first page only"
    assert script.unexpected == [], f"only the requests the pager calls for: {script.unexpected}"
