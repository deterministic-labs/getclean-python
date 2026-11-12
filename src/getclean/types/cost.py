# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .money import Money


class Cost(UniversalBaseModel):
    """
    The money of one call, or of one part of it. `actual` is what you paid, `ceiling` the most this call could have cost, `units` what was counted. On an answer that sums parts, a search with inline fetches or a batch, `source_price` is the sum of the prices every part was asked, and whether each was paid is read from that part's own `cost` and outcome.
    """

    ceiling: typing.Optional[Money] = pydantic.Field(default=None)
    """
    The ceiling applied: the lowest of the request's `max_cost`, the key's cap, the run's budget, the key's budget and the balance; on an operation that takes no `max_cost`, the step's price. Present on every call that can bill.
    """

    actual: Money = pydantic.Field()
    """
    What was billed, a source's price included.
    """

    units: typing.Dict[str, int] = pydantic.Field()
    """
    How many of each unit were billed, keyed by unit name: `contents`, `model_steps`, `screenshots`, `document_pages`, `recognized_pages`, `searches` and `datasource_queries`, an open set. `{}` when nothing was billed.
    """

    source_price: typing.Optional[Money] = pydantic.Field(default=None)
    """
    The price a site or a source asked for this work. getclean pays no site for a page, so a page that asked a price ends `payment_required`, with the price here. Present whenever a price was asked.
    """

    run_budget_remaining: typing.Optional[Money] = pydantic.Field(default=None)
    """
    What is left of the run's budget after this call. Present when the run has a budget.
    """

    key_budget_remaining: typing.Optional[Money] = pydantic.Field(default=None)
    """
    What is left of the key's budget after this call. Present when the key has a budget.
    """

    replayed: bool = pydantic.Field()
    """
    True when this answer is the first answer returned again under the same idempotency key; nothing was billed again.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
