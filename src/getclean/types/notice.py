# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel


class Notice(UniversalBaseModel):
    """
    A fact to read before the result, never an error: something was cut, left out, replaced or found that changes how you read what follows.
    """

    code: str = pydantic.Field()
    """
    What the notice tells you; an open set whose published values are below. A notice kept with the record is a fact of the record and comes back first on every answer about it, with `held` true; the others belong to this answer alone.
    
    | Code | Made by | Means |
    |---|---|---|
    | `highlight_not_found` | the fetch, the upload, the batch, `highlight_contents` | one of your `highlights` strings was not found and nothing bears on it, or `deterministic_only` kept the judging step out; one notice per string, `pointer` naming it, as `/highlights/2`; kept when the fetch made it |
    | `highlights_cut` | the same | more than 50 occurrences were found; the first 50 in document order came; kept |
    | `sections_cut` | the fetch, the upload, the batch, `get_contents`, `get_section` | levels of the map were left out; `get_section` lists them |
    | `links_cut` | the same | the link index was cut at 1,000, or in a batch by `max_total_characters`; `list_links` has the rest |
    | `total_characters_cut` | the batch, the search's inline fetch, the search | this record came as `sections_only` because the whole answer's text bound was reached; `get_contents` returns its text free unless `retention` is `none`; on a search, the excerpts were cut from the last result backwards to fit |
    | `hidden_text_cut` | the fetch, the upload, the batch | a hidden text item was cut at 1,000 characters, or the list at 50 items; kept |
    | `structured_data_cut` | the same | the page's structured data passed 64 KB; kept |
    | `block_over_limit` | `list_blocks` | one block larger than `max_characters` came whole, alone on its page |
    | `page_size_lowered` | every paged answer | `page_size` was above the maximum and was lowered, never refused |
    | `size_limit` | the fetch, the upload, the batch | the page or document passed the largest size taken whole, so the outcome is `too_large`; kept |
    | `conversion_mismatch` | the same | getclean's own check of the text against the page did not pass, so read the content with care; the message carries the two overlap figures it compared; kept |
    | `ad_blocker_failed` | the fetch, the batch | the advertising filter did not run on this read, so advertising may stand among the content; kept |
    | `not_settled` | the fetch, the batch | the page was still changing when `wait_seconds` ran out and was measured as it stood; kept |
    | `unread_region` | the fetch, the upload, the batch | a region that cannot be read as text covers part of the main content; the message names its kind and size; kept |
    | `no_main_content` | the same | no main content was found, so the whole page came under `scope: whole_page`; kept |
    | `paywall_declared` | the fetch, the batch, an uploaded HTML file; repeated by `compare_contents` | the page declares its content not free, so what came may be a teaser; kept |
    | `redirected` | the fetch, the upload by `url`, the batch | the final URL differs from the one asked beyond the scheme, the host's case, a trailing slash and tracking parameters; kept |
    | `requests_blocked` | the fetch, the batch | the page's own requests to addresses that are not globally reachable were blocked and the page went on; the count in the message; kept |
    | `field_not_applicable` | the fetches, the reads of a record, the model steps, the search | a field did not apply to this work and was left out; `field` names it; kept on a search |
    | `cost_cut` | the fetch, the upload, the batch, `highlight_contents`, the search | an extra was cut by `max_cost`, the key's cap or the balance; the message says which, `field` names the extra; kept on a record |
    | `budget_cut` | the same | an extra was cut by the run's or the key's budget; the message says which; kept on a record |
    | `time_cut` | the fetch, the upload, the batch, the search | a model step or the screenshot was cut by `wait_seconds` and not billed; kept |
    | `step_failed` | the fetch, the upload, the batch, `highlight_contents` | a model step or the screenshot failed or passed its bound and was not billed; kept |
    | `model_link_removed` | the fetch, the upload, the batch, `fill_schema`, `summarize_contents` | a link or an image a model wrote was removed from `summary` or `schema_values`; kept |
    | `recognition_uncertain` | the fetch, the upload, the batch | pages were recognized below the published confidence bar; the message names them; kept |
    | `tracked_changes` | the same | the document carries tracked changes, shown as accepted; the count in the message; kept |
    | `upload_to_finish` | the fetch, the batch | a document at a URL was cut by time; `upload_contents` with the `url` parses it whole as a job; kept |
    | `fingerprint_incomparable` | the fetch, the upload, the batch, `compare_contents` | the fingerprint came from another `scope`, version, configuration or kind of source, so the fetch ran whole; on a comparison, the kind of source or the configuration differs and the comparison ran; kept on a fetch's or a batch's record |
    | `fingerprint_unknown` | the fetch, the upload, the batch | the `baseline_fingerprint` matches no record this account keeps, so the fetch ran whole at the full price; kept |
    | `marks_not_read` | the same | the document carries no structure for its formatting, so bold, italics and strikethroughs could not be read; kept |
    | `content_not_rendered` | the same | a page holds handwriting, a drawing, a formula without structure or a blacked-out region, which came flattened or not at all; a published code this version does not make, such content coming with no notice and `pages.pictured` staying `[]` |
    | `archive_unreachable` | the fetch, the batch | an archive did not answer the as-of lookup, so `archives_consulted` lacks it; kept |
    | `default_set_by_policy` | the fetch, the upload, the batch, `highlight_contents`, the search | a default was replaced by the key's policy, as `deterministic_only` under a policy that forbids model work; kept on a record and on a search |
    | `version_retiring` | every answer with notices, except a job, the job list and the catalog | the answer was made under a version within `bounds.contents.version_notice_days` of its retirement |
    | `characters_removed` | a client that cleans the text, never the API | invisible characters, markup comments or hidden words were removed from the text, so the cleaned text no longer hashes to `fingerprint` |
    | `query_corrected` | the search, the search batch | a corrected wording ran beside or instead of yours; `interpretation.wordings` shows it; kept |
    | `filter_emulated` | the same | a source without a filter had it applied afterwards by getclean; the message says how; kept |
    | `window_after_as_of_date` | the same | `published_from` begins after `as_of_date`, so no page can match; kept |
    | `fetch_not_finished` | the same | an inline fetch was not started by the deadline, or its URL is one the key's policy refuses, so its candidate carries no record; kept |
    """

    message: str = pydantic.Field()
    """
    One sentence with the particulars: what was cut, by which limit, how much, or where.
    """

    field: typing.Optional[str] = pydantic.Field(default=None)
    """
    The request field the notice is about. Present when there is one.
    """

    pointer: typing.Optional[str] = pydantic.Field(default=None)
    """
    A JSON Pointer into the request the notice answers: the fetch's request for a notice kept with the record, this call's for its own. Present when there is one.
    """

    datasource_id: typing.Optional[str] = pydantic.Field(default=None)
    """
    The source the notice is about. Present on a search only.
    """

    held: typing.Optional[bool] = pydantic.Field(default=None)
    """
    True on a notice kept with the record, a fact of the work that comes back on every later answer about it. On the fetch's own answer every notice is that answer's own, so none carries it; absent on a notice that belongs to this answer alone.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
