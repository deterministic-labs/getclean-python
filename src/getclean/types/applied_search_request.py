# Generated from the getclean API contract; do not edit.

import datetime as dt
import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .money import Money
from .ranking_order import RankingOrder
from .ranking_priority import RankingPriority
from .retention import Retention
from .safe_search import SafeSearch
from .search_contents_options import SearchContentsOptions
from .source_independence import SourceIndependence
from .subject_identifier import SubjectIdentifier
from .undated import Undated
from .view import View


class AppliedSearchRequest(UniversalBaseModel):
    """
    The request of `search`; also the shape of `Search.applied_request`, the request as it ran with every field in force. Every field is at the top level but the named objects `Money`, `SubjectIdentifier` and `SearchContentsOptions`; an explicit null equals an absent field and gets the default. The object is closed; an unknown field is refused `invalid-field`, `unknown_field`.
    """

    query: typing.Optional[str] = pydantic.Field(default=None)
    """
    The question, 1 to 2,000 characters; required unless `subject_identifiers` is sent. `"phrase"`, `-word`, `OR`, one level of `( )`, `site:`, `filetype:`, `intitle:`, `inurl:`, `before:`, `after:` and `*` are honored where a source supports them, and the receipt's `operators_applied` says what each source did with each.
    """

    alternate_queries: typing.Optional[typing.List[str]] = pydantic.Field(default=None)
    """
    Other wordings of the question, in any language, each 1 to 2,000 characters, up to 10; one merged list with `query`, 20 wordings at most after OR splits. Default none. A wording runs only on the sources that cover its language; nothing is translated, so a wording in another language reaches the sources in that language. Without `query` it is refused `dependent`.
    """

    subject_identifiers: typing.Optional[typing.List[SubjectIdentifier]] = pydantic.Field(default=None)
    """
    Exact codes of the subject, up to 10 `SubjectIdentifier` objects; with no `query`, each identifier's value runs as a wording with origin `identifier`. `issuer` is required for `ticker`, `docket`, `tax_id` and `registry`, as the catalog's codes; a duplicate is refused `duplicate`. Default none.
    """

    subject_country: typing.Optional[str] = pydantic.Field(default=None)
    """
    The country the search is made from, ISO 3166-1 alpha-2; groups of sources expand by it; the inline fetch reads from it when it is a country getclean can read from, one of `Limits.exits`, else from the key's `default_exit` with the notice `field_not_applicable`. Default none.
    """

    purpose: typing.Optional[str] = pydantic.Field(default=None)
    """
    Your reason for the search, kept in the record and read by every model step; never sent to a source. At most 2,000 characters. Default none.
    """

    datasources: typing.Optional[typing.List[str]] = pydantic.Field(default=None)
    """
    Where to search: up to 10 of a datasource id, a group, or `set:NAME`, a published set, each 1 to 64 characters; these are names without dots, where `allowed_domains` takes site names with dots. When sent, the search runs on these plus the sources that resolve a scheme of your `subject_identifiers`, added without a model step, each in the receipt with reason `identifier`. When absent, it runs on `web` plus the groups a model chooses for the question, one model step, each named; under `deterministic_only`, on `web` only. An unknown id is `datasource-unknown`, an unknown set `domain-set-unknown`, a site name here `misplaced`.
    """

    allowed_domains: typing.Optional[typing.List[str]] = pydantic.Field(default=None)
    """
    Only results on these sites count, site names with dots: up to 500 of a domain, a wildcard such as `*.example.com`, a URL prefix, a suffix such as `.gov`, or `set:NAME`, a published set, each 1 to 2,048 characters. What each form reaches: a domain, that host and every host under it; `*.example.com`, the hosts under the domain and not the domain itself; a URL prefix, every address that begins with it; a suffix with a leading dot, every domain that ends in it; `set:NAME`, the sites of that set. It may narrow the key's `policy.allowed_domains` and never widen it, which is `policy-limit-exceeded`. Default none. A site in both this and `blocked_domains` is refused `exclusive`; a datasource id here `misplaced`.
    """

    blocked_domains: typing.Optional[typing.List[str]] = pydantic.Field(default=None)
    """
    Never results on these sites; up to 500 of the same forms and bound as `allowed_domains`, each form reaching what it reaches there. Default none.
    """

    published_from: typing.Optional[dt.date] = pydantic.Field(default=None)
    """
    Pages published on or after this date, inclusive, by the page's own date. Default none. With `published_within_days` it is refused `exclusive`; after `published_until` the pair is refused `order`; a date after today `bound`; a window that begins after `as_of_date` makes the notice `window_after_as_of_date`.
    """

    published_until: typing.Optional[dt.date] = pydantic.Field(default=None)
    """
    Pages published on or before this date, inclusive. Default none.
    """

    published_within_days: typing.Optional[int] = pydantic.Field(default=None)
    """
    Pages published within this many days counted back from today, or from `as_of_date` when it is sent; 1 to 3,650. Not with `published_from` or `published_until`, which is refused `exclusive`. Default none.
    """

    undated: typing.Optional[Undated] = pydantic.Field(default=None)
    """
    Whether pages with no detectable date are kept inside a date window: `shown` keeps them, `hidden` drops them. Default `shown`. Sent without a window it makes the notice `field_not_applicable`.
    """

    languages: typing.Optional[typing.List[str]] = pydantic.Field(default=None)
    """
    Only pages written in these languages, up to 10 BCP 47 tags, each 1 to 35 characters; what the pages are written in, independent of the wordings' languages. Default none.
    """

    media_types: typing.Optional[typing.List[str]] = pydantic.Field(default=None)
    """
    Only these file types, up to 10 IANA media types, each 1 to 255 characters; a bare `pdf` is refused `not_allowed` with `application/pdf` suggested. Default none.
    """

    safe_search: typing.Optional[SafeSearch] = pydantic.Field(default=None)
    """
    How strictly adult content is filtered: `off`, `moderate` or `strict`. Where a source has the setting it is mapped to the nearest level, said with the notice `filter_emulated`; it never removes a source. Never looser than the key's `policy.safe_search`, which is `policy-limit-exceeded`. Default `moderate`.
    """

    source_kinds: typing.Optional[typing.List[str]] = pydantic.Field(default=None)
    """
    Only these kinds of publisher, 1 to 24 of `state`, `court`, `regulator`, `statistics_office`, `intergovernmental`, `standards_body`, `academic`, `scholarly_publisher`, `archive`, `reference`, `press`, `information_provider`, `company`, `professional_practice`, `trade_body`, `marketplace`, `civil_society`, `political`, `religious`, `education`, `healthcare`, `cultural`, `individual`, `community`, never `unknown`; a filter that removes, where `ranking_priorities` only reorders. Default none.
    """

    source_independence: typing.Optional[SourceIndependence] = pydantic.Field(default=None)
    """
    Only sources independent of the subject, or only its own; `independent` or `self`. Needs a subject resolved from `subject_identifiers`, else the notice `field_not_applicable`. Default none, any.
    """

    as_of_date: typing.Optional[dt.date] = pydantic.Field(default=None)
    """
    Search each source as it stood at the end of that day, UTC, and read any inline fetch from an archive's copy of that day. A date not after today. Default none, the sources as they stand now. A source that keeps no history reports `no_history`.
    """

    max_per_datasource: typing.Optional[int] = pydantic.Field(default=None)
    """
    Results taken from each source per wording, before merging; capped by the source's maximum. 1 to 100; default 10.
    """

    ranking_instructions: typing.Optional[str] = pydantic.Field(default=None)
    """
    Your instructions to the ranking model, at most 2,000 characters; kept in the record. Default none. Refused `model-work-refused` under `deterministic_only`.
    """

    ranking_priorities: typing.Optional[typing.List[RankingPriority]] = pydantic.Field(default=None)
    """
    Source facts that go first, in this order, up to 4 of `official`, `independent`, `primary`, `reviewed`; the leads grouped by them, then ordered within each group by `ranking_order`. Default none. `independent` with no subject resolved makes the notice `field_not_applicable`.
    """

    ranking_order: typing.Optional[RankingOrder] = pydantic.Field(default=None)
    """
    The order within each priority group; `relevance`, `newest` or `oldest`; undated pages last under the date orders; the relevance cut-off applies in every case. Default `relevance`.
    """

    ranking_preferred_domains: typing.Optional[typing.List[str]] = pydantic.Field(default=None)
    """
    Sites ranked first among results of equal relevance; other sites still count. Up to 500 of the forms of `allowed_domains`, each reaching what it reaches there, each 1 to 2,048 characters. Default none. A value outside `allowed_domains` when it is set, or in `blocked_domains`, is refused `dependent`.
    """

    ranking_max_per_domain: typing.Optional[int] = pydantic.Field(default=None)
    """
    The most leads kept from one site in the answer, 1 to 50. Default none. With one allowed site it makes the notice `field_not_applicable`.
    """

    max_candidates: typing.Optional[int] = pydantic.Field(default=None)
    """
    The leads returned, 1 to 50; default 10. The results past them are read free by `get_search`.
    """

    max_excerpt_characters: typing.Optional[int] = pydantic.Field(default=None)
    """
    The excerpt per lead, in characters, 0 to 4,000; 0 means none. Default 600.
    """

    max_total_characters: typing.Optional[int] = pydantic.Field(default=None)
    """
    The whole answer's text, excerpts and fetched pages together, 1,000 to 200,000; the excerpts first, cut from the last lead backwards when they alone pass it, then the fetched pages in rank order while they fit in what remains, a page that would pass it coming as `sections_only`; each cut the notice `total_characters_cut`. Default 40,000. Below `max_excerpt_characters` it is refused `order`.
    """

    contents: typing.Optional[SearchContentsOptions] = pydantic.Field(default=None)
    """
    Fetch this many top leads in the same call, under the inline fetch's rules; `contents.max_characters` bounds one page, `max_total_characters` the whole answer. Default none. The options without `top` are refused `required`; `top` above `max_candidates` `order`; with `wait_seconds` below 5, the least a fetch needs, `order`.
    """

    view: typing.Optional[View] = pydantic.Field(default=None)
    """
    How much of the record comes back: `full`, every member, or `compact`, the smaller form the `Search` schema lists. Default `full`.
    """

    wait_seconds: typing.Optional[float] = pydantic.Field(default=None)
    """
    The most seconds this call may work, the ranking, the choice of sources and every inline fetch inside, counted from the start of the work; what did not finish comes back `partial`, named. 0.2 to 60; default 10.
    """

    max_cost: typing.Optional[Money] = pydantic.Field(default=None)
    """
    The most this call may cost, in the account's currency. When it cannot cover everything, the extras are cut in order, each with the notice `cost_cut`: first each inline fetch's own extras, then whole fetches, then the ranking, then the choice of sources, then the results taken per source. Default the key's cap on one call. Below the smallest call's price, one `searches` and one `datasource_queries`, it is refused `cost-exceeds-cap` with `minimum_cap`.
    """

    deterministic_only: typing.Optional[bool] = pydantic.Field(default=None)
    """
    Turn off every step a model judges: the ranking and the choice of sources, which the answer then says; the publisher's kind only from what getclean already knows; the inline fetch's `json_schema` and `summary` refused by name and its `highlights` found verbatim only. Text recognition on a scanned page fetched inline still runs and is listed. Default false. Sending false under a key whose policy forbids model work is `policy-limit-exceeded`.
    """

    pinned_version: typing.Optional[str] = pydantic.Field(default=None)
    """
    The version of getclean to run under, at most 64 characters. Default the current version. A version not served is `version-withdrawn`.
    """

    run_id: typing.Optional[str] = pydantic.Field(default=None)
    """
    The run the record belongs to, an existing run of the key. Default the key's default run. An unknown run is refused `not_allowed`.
    """

    record_form: typing.Optional[str] = pydantic.Field(default=None)
    """
    Have the search written up for a reviewer: `plain`, in plain words, or `prisma`, in the PRISMA form a systematic review reports; an open set. Default none, no write-up.
    """

    metadata: typing.Optional[typing.Dict[str, str]] = pydantic.Field(default=None)
    """
    Your own labels, returned on the record as sent and never passed to a source: at most 20 string pairs, keys of 1 to 64 characters, values of 1 to 512. Default none. An empty map is refused `bound`.
    """

    max_source_price: typing.Optional[Money] = pydantic.Field(default=None)
    """
    The most you allow for a datasource that charges per query, or for a site an inline fetch meets that asks a price. A source whose fee passes it is not searched, the coverage gap `over_price`, never a refusal. getclean pays no site for a page, so a page that asks a price ends `payment_required`. Default none.
    """

    retention: typing.Optional[Retention] = pydantic.Field(default=None)
    """
    How long the search record and every inline record are kept: `hold`, 48 hours after the last call and at most 30 days, allowed only under a `hold` policy; `none`, nothing kept past the answer. Default the key's `policy.retention`.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
