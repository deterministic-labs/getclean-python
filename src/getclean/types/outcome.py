# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .outcome_kind import OutcomeKind


class Outcome(UniversalBaseModel):
    """
    What happened to one piece of work, first in every answer. A record's outcome is the fact of the call that made it, and no later read rewrites it.
    """

    kind: OutcomeKind = pydantic.Field()
    """
    What kind of thing happened, one of five: `delivered`, everything asked for came, or the map of sections came in place of text that did not fit; `partial`, the work stopped in the middle and what was done is kept; `failed`, the source did not give a page; `refused`, a rule stopped the read; `needs_person`, a person must act before this can work. A closed set.
    """

    reason: str = pydantic.Field()
    """
    Why it happened. An open set whose published values are below; each line says what the reason means and what may work next, and `message` carries that sentence when the reason has one.
    
    The contents family, the record of one source:
    
    | Reason | Kind | Means | What may work next |
    |---|---|---|---|
    | `whole` | delivered | everything asked for fit | |
    | `sections_only` | delivered | the text did not fit `max_characters`, so the map of sections came instead | `get_section` on a row, free |
    | `matching_sections` | delivered | the text did not fit; the sections holding your highlights came | `get_section` for the rest |
    | `unchanged` | delivered | the page matches your `baseline_fingerprint`; no text is sent, the fetch's price is billed | |
    | `pages_failed` | partial | some pages of a document could not be parsed; `pages.failed_pages` names them | |
    | `cost_capped` | partial | the parse stopped at `max_cost`, the key's cap or the balance; `message` says which | a larger `max_cost`, or the account owner funds the account or raises the cap |
    | `budget_capped` | partial | the parse stopped at the run's or the key's budget | the account owner raises the budget |
    | `time_capped` | partial | a document at a URL did not finish within `wait_seconds`, or a job passed its bound | `upload_contents` with the `url`, which parses it whole as a job |
    | `canceled` | partial | the job was canceled with pages already parsed; they are kept | |
    | `dns_timeout`, `connection_refused`, `connection_timeout`, `connection_terminated`, `tls_protocol_error`, `http_response_timeout`, `http_response_incomplete` | failed | the fetch failed on the way to the site, named as RFC 9209 names it | a retry later may work |
    | `dns_error`, `tls_certificate_error` | failed | the site's name did not resolve, or its certificate failed | the same request will not work |
    | `not_found` | failed | the site answered 404 or 410 | the same request will not work |
    | `access_denied` | failed | the site answered 401 or 403 | the same request will not work |
    | `payment_required` | failed | the site asked a price at the request, or answered 402, and no `max_source_price` covered it; `cost.source_price` is the price asked | a `max_source_price` |
    | `rate_limited` | failed | the site answered 429 | a retry later may work |
    | `server_error` | failed | the site answered 5xx | a retry later may work |
    | `http_error` | failed | another status that is not a page | the same request will not work |
    | `challenge_served` | failed | a bot challenge stood where the page should be | a retry later may work on sites that do not challenge every new visitor; or a person opens the URL and uploads the saved page with `captured_url` |
    | `blocked` | failed | the site refused the visitor with a block page | the same request will not work |
    | `region_restricted` | failed | the page says it is not offered in the visitor's country | another `subject_country` |
    | `deadline` | failed | nothing readable by `wait_seconds` | a larger `wait_seconds` |
    | `empty` | failed | no text, no links and nothing to recognize | the same request will not work |
    | `corrupt_document` | failed | the document could not be opened | the same request will not work |
    | `no_history` | failed | no archive copy at or before the end of `as_of_date`; `source.archives_consulted` names the archives asked | the same date will not work |
    | `too_large` | refused | the page or document passed the largest size taken whole; for a document, `pages.count` and the outline still come | the same request will not work |
    | `destination_refused` | refused | the address resolved to, or a redirect reached, a place that is not globally reachable | the same request will not work |
    | `domain_not_allowed` | refused | a redirect reached a host outside the key's domain policy | the same request will not work under this key's policy |
    | `unsupported_media_type` | refused | a document type not taken, a container or a media file; or, on the upload, a `url` that serves a web page, where `fetch_contents` is the call | the same request will not work |
    | `password_protected` | refused | the document is locked | a person with the password |
    | `robots_disallowed` | refused | the site's robots file forbids getclean by its published name | the same request will not work |
    | `robots_unreachable` | refused | the robots file answered 5xx or not at all, which RFC 9309 reads as a full disallow | a retry later may work |
    | `legal_block` | refused | the site answered 451; `source.blocked_by` carries its link | another source, never another `subject_country` |
    | `sign_in_needed` | needs_person | a sign-in page stood where the page should be | a person signs in and uploads the saved page with `captured_url` |
    | `paywalled` | needs_person | a purchase wall stood where the page should be | a person |
    
    The search family, the search as a whole and each source's receipt:
    
    | Reason | Kind | Means | What may work next |
    |---|---|---|---|
    | `candidates` | delivered | one or more results | |
    | `none` | delivered | nothing matched; the receipt says what was searched | other wordings |
    | `corrected_question` | delivered | every result came for a wording getclean corrected; `interpretation.wordings` shows the correction | |
    | `sources_missing` | partial | a source or a wording gave no list while others did | a retry later may work for that source |
    | `rerank_missing` | partial | the deadline or the ceiling cut the reranking; the merged order came and `relevance_score` is null | a larger `wait_seconds` or `max_cost` |
    | `fetches_missing` | partial | some inline fetches did not finish or were cut; the notice `fetch_not_finished` names the candidates | `fetch_contents` on each |
    | `not_accepted_by_source` | failed | every source refused the question as written; a source's own words stand in `source_text` | another wording |
    | `source_unreachable` | failed | every source was down | a retry later may work |
    | `legal_block` | refused | a source withheld by law | another source |
    | `login_expired` | needs_person | a registered login expired | the account owner renews the login |
    | `fee_through_form` | needs_person | the source charges only through a form | a person |
    
    In a source's receipt, `datasources_searched[].outcome`, the failed reasons of the first table name what happened to that one source, with `deadline` for a source that had not answered at `wait_seconds` and `payment_required` for a fee above `max_source_price`; `legal_block` and `domain_not_allowed` refuse a source withheld by law or outside the key's domain policy.
    """

    message: typing.Optional[str] = pydantic.Field(default=None)
    """
    One sentence with the particulars a reason has, the limit that stopped the work, the protocol that asked a price, the operation to use instead, and on a reason that has retry guidance, that guidance's sentence. Present when the reason has any.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
