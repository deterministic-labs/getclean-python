"""The client's signatures against the base client's. Each method the client writes again or adds takes the parameters
of the base method it wraps or stands beside, in the same order, with the same types and defaults, and only what it adds
beside them; the methods the client takes over are the calls that may bill, those whose base method takes an
idempotency key, and the two lists that grow while they page, and nothing else."""

import inspect
import os
import typing

import pytest

from getclean import AsyncGetClean, GetClean
from getclean.base_client import AsyncBaseGetClean, BaseGetClean

BOTH = pytest.mark.parametrize(
    "client_class, base_class",
    [(GetClean, BaseGetClean), (AsyncGetClean, AsyncBaseGetClean)],
    ids=["GetClean", "AsyncGetClean"],
)

GROWING_LISTS = {"list_jobs", "list_contents"}
"""The two lists that grow while they page, whose pagers drop repeats."""


class Parameter(typing.NamedTuple):
    """A parameter as a caller meets it: its name, how it is passed, its type with every name resolved, its default."""

    name: str
    kind: typing.Any
    annotation: typing.Any
    default: typing.Any


def parameters(function: typing.Any) -> typing.List[Parameter]:
    """The parameters of a function, in order, each type resolved by typing.get_type_hints."""
    hints = typing.get_type_hints(function)
    return [
        Parameter(p.name, p.kind, hints.get(p.name, p.annotation), p.default)
        for p in inspect.signature(function).parameters.values()
    ]


def methods(base_class: type) -> typing.Set[str]:
    """The base client's public methods: the API's operations, and close."""
    return {name for name, value in vars(base_class).items() if inspect.isfunction(value) and not name.startswith("_")}


def billed(base_class: type) -> typing.Set[str]:
    """The calls that may bill: the base methods that take an idempotency key."""
    return {
        name
        for name in methods(base_class)
        if "idempotency_key" in inspect.signature(getattr(base_class, name)).parameters
    }


@BOTH
def test_the_client_takes_over_the_billed_calls_and_the_growing_lists_and_nothing_else(
    client_class: typing.Any, base_class: typing.Any
) -> None:
    """The base methods the client writes again are the calls that may bill, the eight whose base method takes an
    idempotency key, and list_jobs and list_contents, and no other."""
    taken_over = {name for name in vars(client_class) if not name.startswith("_") and name in methods(base_class)}

    assert len(billed(base_class)) == 8, f"eight calls may bill: {sorted(billed(base_class))}"
    assert taken_over == billed(base_class) | GROWING_LISTS, (
        f"the client takes over the billed calls and the growing lists, and nothing else: {sorted(taken_over)}"
    )


@BOTH
def test_the_client_adds_iter_section_and_no_other_method(client_class: typing.Any, base_class: typing.Any) -> None:
    """The one method the client adds beside the base's is iter_section, the section pager."""
    added = {
        name
        for name, value in vars(client_class).items()
        if not name.startswith("_") and callable(value) and not hasattr(base_class, name)
    }

    assert added == {"iter_section"}, f"the client adds iter_section alone: {sorted(added)}"


@BOTH
def test_the_constructor_takes_the_base_constructors_parameters(
    client_class: typing.Any, base_class: typing.Any
) -> None:
    """The client is built with the base client's parameters, in the same order, with the same types and defaults."""
    assert parameters(client_class.__init__) == parameters(base_class.__init__), (
        "the constructor's parameters equal the base constructor's"
    )


@BOTH
@pytest.mark.parametrize("method", sorted(billed(BaseGetClean) - {"upload_contents"}))
def test_a_billed_call_takes_the_base_methods_parameters(
    client_class: typing.Any, base_class: typing.Any, method: str
) -> None:
    """Each call that may bill, the upload aside, takes its base method's parameters, in the same order, with the same
    types and defaults, and returns what the base method returns."""
    ours, theirs = getattr(client_class, method), getattr(base_class, method)

    assert parameters(ours) == parameters(theirs), f"{method} takes its base method's parameters"
    assert typing.get_type_hints(ours)["return"] == typing.get_type_hints(theirs)["return"], (
        f"{method} returns what its base method returns"
    )


@BOTH
@pytest.mark.parametrize("method", sorted(GROWING_LISTS))
def test_a_growing_list_takes_the_base_methods_parameters(
    client_class: typing.Any, base_class: typing.Any, method: str
) -> None:
    """list_jobs and list_contents take their base methods' parameters, in the same order, with the same types and
    defaults, and return the same pager."""
    ours, theirs = getattr(client_class, method), getattr(base_class, method)

    assert parameters(ours) == parameters(theirs), f"{method} takes its base method's parameters"
    assert typing.get_type_hints(ours)["return"] == typing.get_type_hints(theirs)["return"], (
        f"{method} returns the base method's pager"
    )


@BOTH
def test_the_upload_takes_the_base_uploads_parameters_and_wait(
    client_class: typing.Any, base_class: typing.Any
) -> None:
    """upload_contents takes the base upload's parameters, in the same order, with the same types and defaults, and adds
    wait, off by default, before request_options; its document takes what the base upload takes and a path besides, an
    os.PathLike."""
    ours = {p.name: p for p in parameters(client_class.upload_contents)}
    theirs = {p.name: p for p in parameters(base_class.upload_contents)}

    assert list(ours) == [*list(theirs)[:-1], "wait", "request_options"], (
        f"the base upload's parameters in their order, and wait before request_options: {list(ours)}"
    )
    assert ours["wait"].annotation is bool and ours["wait"].default is False, "wait is a bool, off by default"
    widened = set(typing.get_args(ours["document"].annotation)) - set(typing.get_args(theirs["document"].annotation))
    assert widened == {os.PathLike[str]}, f"document takes the base upload's forms and an os.PathLike: {widened}"
    assert set(typing.get_args(theirs["document"].annotation)) <= set(typing.get_args(ours["document"].annotation)), (
        "document takes every form the base upload takes"
    )
    differing = [
        f"{name}: {ours[name].annotation} = {ours[name].default!r} against {theirs[name].annotation} = "
        f"{theirs[name].default!r}"
        for name in theirs
        if name != "document"
        and (ours[name].annotation, ours[name].default) != (theirs[name].annotation, theirs[name].default)
    ]
    assert differing == [], f"every other parameter has the base upload's type and default: {differing}"
    assert (
        typing.get_type_hints(client_class.upload_contents)["return"]
        == typing.get_type_hints(base_class.upload_contents)["return"]
    ), "upload_contents returns what the base upload returns"


@BOTH
def test_iter_section_takes_what_get_section_takes(client_class: typing.Any, base_class: typing.Any) -> None:
    """iter_section takes get_section's parameters, page_token among them, in the same order, with the same types and
    defaults."""
    assert parameters(client_class.iter_section) == parameters(base_class.get_section), (
        "iter_section takes what get_section takes, page_token included"
    )
