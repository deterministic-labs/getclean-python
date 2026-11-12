# Generated from the getclean API contract; do not edit.

import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .bound import Bound


class Bounds(UniversalBaseModel):
    """
    The published bounds, one map per family. A key is a request field, for the bound most operations share; `<operation>.<field>` for an operation whose bound differs; or one of the service's own limits. Each value is a `Bound` with its least, greatest and default value.
    """

    contents: typing.Dict[str, Bound] = pydantic.Field()
    """
    The contents family's bounds, by key.
    
    | Key | Bounds |
    |---|---|
    | `max_characters` | the text returned by a fetch, an upload, a batch item or a read: 0 for the map alone, or 1,000 to 1,000,000; default 20,000 |
    | `list_blocks.max_characters` | the text of one page of `list_blocks`: 1,000 to 1,000,000; default 20,000 |
    | `max_total_characters` | the text of a whole batch answer: 1,000 to 2,000,000; default 200,000 |
    | `wait_seconds` | the seconds a fetch or an upload may work: 5 to 90; default 30 |
    | `get_job.wait_seconds` | the seconds `get_job` waits for a job to finish: 0 to 90; default 0 |
    | `page_size` | items per page of a list: 1 to 200; default 50 |
    | `items` | fetches in one batch: 1 to 20 |
    | `highlights` | strings in `highlights`: 1 to 5, each at most 4,000 characters |
    | `recognition_languages` | languages named for recognition: 1 to 10 |
    | `call_seconds` | the most seconds one call may take in all; set your client's timeout above it |
    | `batch_seconds` | the most seconds a batch call runs; an item not started by then is skipped |
    | `queue_seconds` | the most seconds a request may wait to start before `503 overloaded` |
    | `model_step_seconds` | the most seconds one model step may take; past it the step is cut, or `504` when it is the whole call |
    | `screenshot_seconds` | the most seconds the screenshot may take |
    | `screenshot_bytes` | the largest screenshot sent inline under `retention: none` |
    | `job_seconds` | the most seconds a job runs, 30 minutes; past it the record is `partial`, `time_capped` |
    | `read_seconds` | the most seconds a read of a record you already have may take |
    | `page_bytes` | the largest page taken whole, and the most bytes of `raw_html` sent inline |
    | `document_bytes` | the largest document, 100 MiB |
    | `document_base64_bytes` | the largest document a base64 argument may carry, 20 MiB |
    | `document_pages` | the most pages of a document |
    | `document_page_characters` | the characters counted as one page on a format without pages |
    | `body_bytes` | a JSON body, 256 KB |
    | `batch_body_bytes` | a batch body, 4 MiB |
    | `compare_body_bytes` | a comparison body, 8 MiB |
    | `redirects` | the most redirect hops followed |
    | `links` | the link index a fetch returns, 1,000; `list_links` has the rest |
    | `section_rows` | the map's rows below the first level under `max_characters: 0`, 200 |
    | `highlight_occurrences` | occurrences of a highlight string per call, 50 |
    | `summary_characters` | a summary's length, 1,500 |
    | `structured_data_bytes` | a page's structured data, 64 KB |
    | `recognition_confidence_min` | the confidence below which a recognized page is noticed `recognition_uncertain` |
    | `version_notice_days` | the days of notice before a version retires, during which `version_retiring` is sent |
    """

    search: typing.Dict[str, Bound] = pydantic.Field()
    """
    The search family's bounds, by key.
    
    | Key | Bounds |
    |---|---|
    | `max_candidates` | results returned: 1 to 50; default 10 |
    | `max_per_datasource` | results taken from each source per wording: 1 to 100; default 10 |
    | `max_excerpt_characters` | the excerpt per result: 0 to 4,000; default 600 |
    | `max_total_characters` | the whole answer's text, excerpts and fetched pages together: 1,000 to 200,000; default 40,000 |
    | `wait_seconds` | the seconds a search may work: 0.2 to 60; default 10 |
    | `get_search.page_size` | results per page of a search you already have: 1 to 50; default the search's `max_candidates` |
    | `list_datasources.page_size` | entries per page of the catalog: 1 to 200; default 50 |
    | `items` | searches in one batch: 1 to 20 |
    | `datasources` | sources named in one search: up to 10 |
    | `alternate_queries` | other wordings in one search: up to 10 |
    | `call_seconds` | the most seconds one call may take in all |
    | `batch_seconds` | the most seconds a batch call runs; an item not started by then is skipped |
    | `queue_seconds` | the most seconds a request may wait to start before `503 overloaded` |
    | `model_step_seconds` | the most seconds the reranking or the discovery step may take |
    | `body_bytes` | a JSON body, 256 KB |
    | `batch_body_bytes` | a batch body, 4 MiB |
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
