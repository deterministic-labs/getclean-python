# Reference
<details><summary><code>client.<a href="src/getclean/client.py">list_contents</a>(...) -> SyncPager[ContentsCompact, ContentsPage]</code></summary>
<dl>
<dd>

#### Description

<dl>
<dd>

<dl>
<dd>

List the records the account keeps, newest first, free. Each item is a `ContentsCompact`: the record's id, outcome, source and dates, with no text, no map, no model work and no cost, and its `execution` as stored.

Use it to see which pages the account already has before fetching one again; `get_contents` reads one record whole. Every filter you send must match. The list does not move any record's `expires_at`.

**What it costs.** The key needs `contents:read`. The call is free. The answer is `200` with `ContentsPage`.

**Paging.** `page_size` from 1, default 50, maximum 200; a value above the maximum is lowered with the notice `page_size_lowered` and never refused; a value below 1 is refused `bound`. `page_token` is opaque, bound to its query, alive 24 hours; `next_page_token` is absent on the last page, and a page that carries it holds at least one record. A changed filter between pages, `page_size` excepted, or an unknown, expired or another list's token, is `400 page-token-invalid` with `change.field` naming `page_token`: drop the token and start again. A record made while you page may make an item repeat; when you merge pages, keep one entry per `id`.

**Refused before any work.** A value outside its set or range, `page_size` above its maximum excepted, which is lowered: `400 invalid-request`, `not_allowed` or `bound`, each with where it is. A `run_id` of the wrong form: `400 invalid-request`, `syntax`; an unknown run: `400 invalid-request`, `not_allowed`, since a run is a setting of the key and not a resource here. A token of another list: `400 page-token-invalid`. An unknown query parameter: `400 invalid-request`, `unknown_field`.

**Notices this operation makes.** `page_size_lowered`, `version_retiring`.

**Problem types.**
- 400 `invalid-request`, The request is invalid; `page-token-invalid`, The page token is invalid.
- 401 `unauthorized`, The key is missing or rejected.
- 403 `insufficient-scope`, The key lacks a scope this call needs.
- 429 `rate-limit-exceeded`, The rate limit is exceeded; `concurrency-limit-exceeded`, Too many calls are in flight.
- 500 `internal-error`, The service failed.
- 503 `overloaded`, The service is overloaded.
</dd>
</dl>
</dd>
</dl>

#### Usage

<dl>
<dd>

<dl>
<dd>

```python
from getclean import GetClean
from getclean.environment import GetCleanEnvironment

client = GetClean(
    environment=GetCleanEnvironment.PRODUCTION,
)

client.list_contents(
    url="https://example.com/*",
    carrier="web",
    run_id="run_default",
)

```
</dd>
</dl>
</dd>
</dl>

#### Parameters

<dl>
<dd>

<dl>
<dd>

**url:** `typing.Optional[str]` — Only records whose `source.url` equals it, or starts with it when it ends in `*`, the one place a `*` may stand; the scheme and the host are compared in lower case. At most 2,048 characters. Default none.
    
</dd>
</dl>

<dl>
<dd>

**carrier:** `typing.Optional[str]` — Only records of this kind of source: `web`, a live page; `archive`, an archive's copy read under `as_of_date`; `upload`, bytes you sent. An open set. Default none.
    
</dd>
</dl>

<dl>
<dd>

**run_id:** `typing.Optional[str]` — Only records of this run, an existing run of the key. Default none.
    
</dd>
</dl>

<dl>
<dd>

**page_size:** `typing.Optional[int]` — At most this many records on the page, from 1; default 50; the maximum, 200, stands in `Limits.bounds`, and a larger value is lowered with the notice `page_size_lowered`.
    
</dd>
</dl>

<dl>
<dd>

**page_token:** `typing.Optional[str]` — The next page, as the last answer's `next_page_token` gave it; opaque, at most 1,024 characters, never built by the caller. Default none, the first page.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/getclean/client.py">fetch_contents</a>(...) -> Contents</code></summary>
<dl>
<dd>

#### Description

<dl>
<dd>

<dl>
<dd>

Fetch a web page or a document at a URL. You get its main content with the structure intact, in the formats you ask for, the map of its sections, the facts of the source, a fingerprint and the price, as one record that is kept for later reads.

The record is kept 48 hours after its last call and at most 30 days from its making, and every later question about it, through `get_contents`, `get_section`, `list_blocks` and `list_links`, is answered from the same copy, free. Use `upload_contents` for a file you hold, or for a long document that must run as a job; use `search` when you have a question and no URL yet; use `get_contents` to read a record you already have.

**What it costs.** The key needs `contents:fetch`, plus `contents:model` when you send `json_schema`, set `summary` or send `highlights` without `deterministic_only`; getclean decides this from the request before any work, so a missing scope is `403` before any `422`. The price is 1 `contents`, plus `document_pages` and `recognized_pages` when the URL serves a document, plus `model_steps` for each model field that ran, plus `screenshots` when one was made. An `unchanged` answer bills the same 1 `contents`. A fetch that failed, was refused or needs a person bills nothing.

**What comes back.** `201 Created`, with `Location` naming the record, for every outcome kind: a page that could not be read is still a record, whose `outcome` says what happened and what may work next. The record carries what happened, the notices to read first, when the fetch ran, its fingerprint, the content or the map, the facts of the source and the price.

**The idempotency key.** `Idempotency-Key` is optional here. The same key with the same body returns the first answer again, with this call's `request_id`, `expires_at` as it stands and `replayed` true on `cost`; nothing is billed again. The same key while the first call still runs is `409 idempotency-key-in-flight`; the same key with another body is `422 idempotency-key-reused`. A replay whose record was deleted is `404 not-found` naming the deletion.

**How the text fits `max_characters`.**
- It fits: the text formats come whole; the reason is `whole`; `truncated` is false.
- It does not fit: no text format comes; `sections`, the map, comes instead; the reason is `sections_only`; `truncated` is true. `screenshot` and `raw_html` still come.
- It does not fit and a highlight was found: the sections that hold highlights come in document order while they fit; a section larger than what remains is cut at a block edge with its highlighted blocks inside; the map comes too, as with `max_characters: 0`, and does not count against the limit; the reason is `matching_sections`; `truncated` is true; `get_section` has the rest.
- `max_characters: 0`: no text; the map comes; the reason is `whole`; `truncated` is false; `screenshot`, `raw_html` and `links` still come, the links within their cap.
- The map always carries level 1 and `s0`, however many rows. Deeper levels come one whole level at a time from the top, while their rows fit `max_characters`; under `0`, while the rows number at most 200. The notice `sections_cut` says when levels were left out.
- Two text formats each carry the whole content, so the answer is twice as long; `max_characters` bounds the content once, and each format carries it.
- A sent `max_characters` with no text format bounds nothing and makes the notice `field_not_applicable`; the default makes none. `links`, `screenshot` and `raw_html` are outside it.
- To learn a document's size and price for one `contents` unit, send `max_characters: 0` with `max_cost` at the smallest call's price: no page is parsed beyond the count and the outline.

**The formats.** `block_kinds` narrows every format: the text formats and `links` hold only those blocks, and `highlights`, `json_schema` and `summary` read only those blocks; `whole` then means all of them fit; `counts` stays the page's. `scope: whole_page` makes the blocks, the sections and the counts cover the whole page, and `left_out` is `[]`. A highlight is marked `<mark id="h1">…</mark>` in `markdown` and `html` and listed in `highlight_ids` on `blocks`; nothing is marked in `doclang`, `links`, `screenshot` or `raw_html`; with no text returned, the `highlights` list still comes with its ids and places. Every occurrence of a string is a highlight, in document order, at most 50 per call, with the notice `highlights_cut` past that. `highlights`, `json_schema` and `summary` read the whole content, or the chosen blocks, whatever `max_characters` says; the bound limits what is returned, not what they read. `summary` is at most 1,500 characters, in the content's language. `summary` and `schema_values` carry no link and no image; any a model writes is removed with the notice `model_link_removed`, and a URL value is kept only when it stands in the record's links or text.

**Each highlight string.**
- Found `exact`: its words stand in one block, after Unicode normalization and whitespace collapse, case kept. Free.
- Found `near`: its words stand there after case folding, with ellipses and the punctuation at the ends of words removed, punctuation inside a word kept, pieces in order, and the dotted and dotless i of Turkic scripts folded to one. Free.
- Not found verbatim: a model picks the blocks that bear on it, `judged`. One model step per call, however many strings needed it.
- Not found, and nothing bears on it, or `deterministic_only`: the notice `highlight_not_found`, one per string. The step's price when a model judged it, free under `deterministic_only`.

**`deterministic_only`.** Nothing runs whose output could differ between two runs of the same input: highlights are found verbatim only; `json_schema` and `summary` are refused as `model-work-refused`, both fields named in `violations`; the publisher's kind comes only from what getclean already knows. Text recognition on a scanned page still runs and is listed, since it repeats under one version. A key whose policy forbids model work refuses `json_schema` and `summary` with `policy-limit-exceeded` and finds highlights verbatim only; `deterministic_only: false` under such a key is `policy-limit-exceeded`, since a request never loosens the key.

**`baseline_fingerprint`.** On a page: the page is read in full and its fingerprint compared. If it matches, the answer is `unchanged`: no text, no highlights, no fill, no summary, `formats` echoed `[]`, while the record keeps the content, which `get_contents` reads. On a document at a URL: the bytes are fetched; when a record of your account issued the fingerprint you sent and its `document_digest` equals the bytes' digest, the answer is `unchanged` without a parse; otherwise the parse runs and bills its pages, and a matching content fingerprint then answers `unchanged`. If no record of your account issued the fingerprint, you get the notice `fingerprint_unknown`, and the fetch runs whole at the full price. A fingerprint matches only under the scope, the version, the configuration and the kind of source that made it; one issued under another makes the notice `fingerprint_incomparable`, naming which, and the fetch runs whole at the full price. A fingerprint of a record no longer kept is `fingerprint_unknown` too, so an agent that comes back after its record expired pays the full price and compares fingerprints itself.

**`as_of_date`.** The record is an archive copy: `source.carrier` is `archive`, `source.archive` names the copy, and `source.archives_consulted` names the archives of `Limits.archives` that answered. The copy is the latest capture at or before 23:59:59 UTC of that day whose archived status was 2xx, so a capture later on that day may come, `archive.captured_at` showing when; an agent that needs the state before an event asks for the day before. `source.next_capture_at` comes when a later capture exists, so an agent steps forward capture by capture. No such copy is `no_history`. `subject_country`, `subject_language`, `screenshot` and `max_source_price` are not applied to an archive copy, a notice each.

**`screenshot` and `raw_html`.** The screenshot is of the live page only: the whole page at its full width, as PNG, with its digest, by a URL getclean serves for as long as the record lives. It ignores `scope` and `block_kinds`. It is taken on a second visit to the page, which may be served another page. `raw_html` is the page's bytes exactly as the server sent them, decompressed, before any script ran, on an archive copy as the archive served them, with their digest, their size and the `Content-Type` sent; by a URL under `retention` `hold`, inline as `data_base64` under `none`. It ignores `scope`, `block_kinds` and `max_characters`, and it is free. The served bytes and their digest let you show later exactly what the server sent.

**A document at the URL.** It is parsed inside the fetch. Past `wait_seconds` the pages parsed come back `partial`, `time_capped`, with the notice `upload_to_finish`; past `max_cost` they come back `partial`, `cost_capped`. `pages.count` and the outline come even when no page was parsed.

**Money, country and version.** `max_cost` is reserved at the start against the ceiling: the lowest of `max_cost`, the key's cap, the run's budget, the key's budget and the balance. It is spent in one order, the read of the page or of the document's pages first, then `json_schema`, `highlights`, `summary` and `screenshot`. When the ceiling, a budget or the deadline cannot cover everything, the extras are cut from the end, each cut a notice naming the field, and the pages are stopped last, the record `partial`. A run's or a key's budget that stops a parse is `budget_capped`, with the notice `budget_cut`. `max_source_price`: getclean pays no site, whatever the value; a site that asks a price ends `failed`, `payment_required`, with the price in `cost.source_price` and the protocol named in the message. `subject_country` is the country the page is read from; a page that says it is not offered there is `region_restricted`, and a site that refuses the visitor with a block page is `blocked`. `pinned_version`: `execution.version` equals it.

**Fields that do not apply to some sources.** Each is a notice `field_not_applicable` naming the field, never a refusal, so a client that always sends a field still works on every source:
- `doclang`, `screenshot`, `raw_html` or `scope: whole_page` on a URL that serves a document;
- `recognition_languages` on a web page;
- `subject_country`, `subject_language`, `screenshot` or `max_source_price` with `as_of_date`;
- a sent `max_characters` with no text format;
- `block_kinds` with nothing to narrow.

The table under `Contents` says which members each kind of source carries.

**Refused before any work**, every violation of the body reported at once in `violations`:
- `scope`, a `formats` value, a `block_kinds` value or `retention` outside its set: `invalid-field`, `not_allowed`.
- A duplicate in `formats` or `block_kinds`: `duplicate`. An empty `block_kinds` list: `bound`; send `formats: []` for the facts alone.
- `max_characters` between 1 and 999: `bound`.
- `json_schema` or `summary` under the request's `deterministic_only`: `model-work-refused`, both fields named.
- `json_schema`, `summary` or `deterministic_only: false` under a key whose policy forbids model work: `403 policy-limit-exceeded`.
- `max_cost` below the smallest call's price: `cost-exceeds-cap`, with `minimum_cap`.
- A scheme other than http or https, a password in the URL's userinfo, or a malformed `baseline_fingerprint`: `syntax`.
- localhost, an address that is not globally reachable, or a port the Fetch standard lists as bad: `destination-refused`.
- A host outside the key's domain policy, or a URL the key's `policy.refuse_credential_urls` refuses: `403 policy-limit-exceeded`.
- A `subject_country` getclean cannot read from: `not_allowed`, with the countries it can read from in `allowed_values`.
- A `json_schema` that is not valid JSON Schema 2020-12: `syntax`. One whose root is not `type: object`, that has no `properties`, or whose `pattern` needs backtracking: `not_allowed`.
- An unknown `run_id`: `not_allowed`. `retention: hold` under a `none` policy: `403 policy-limit-exceeded`.
- A missing `url`: `required`. Any other bound passed: `bound`. An unknown field: `unknown_field`.
- `pinned_version` not served, never or no longer: `version-withdrawn`, with the versions served.

The one exclusive pair is `deterministic_only` against `json_schema` and `summary`. No dependent field refuses; `block_kinds` with nothing to narrow is a notice. Every other pair is independent.

**Notices this operation makes.** `highlight_not_found`, `highlights_cut`, `sections_cut`, `links_cut`, `hidden_text_cut`, `structured_data_cut`, `size_limit`, `conversion_mismatch`, `ad_blocker_failed`, `not_settled`, `unread_region`, `no_main_content`, `paywall_declared`, `redirected`, `requests_blocked`, `field_not_applicable`, `cost_cut`, `budget_cut`, `time_cut`, `step_failed`, `model_link_removed`, `recognition_uncertain`, `tracked_changes`, `upload_to_finish`, `fingerprint_incomparable`, `fingerprint_unknown`, `marks_not_read`, `archive_unreachable`, `default_set_by_policy`, `version_retiring`. `content_not_rendered` is a published code this version does not make.

**Problem types.**
- 400 `invalid-request`, The request is invalid.
- 401 `unauthorized`, The key is missing or rejected.
- 403 `insufficient-scope`, The key lacks a scope this call needs; `policy-limit-exceeded`, The key's policy forbids this; `credit-exhausted`, The credit is exhausted; `run-budget-exhausted`, The run's budget is exhausted; `key-budget-exhausted`, The key's budget is exhausted.
- 404 `not-found`, Not found, on a replay whose record was deleted.
- 409 `idempotency-key-in-flight`, The same request is still running.
- 413 `body-too-large`, The body is too large.
- 415 `unsupported-media-type`, The media type is not supported.
- 422 `invalid-field`, A field is invalid; `destination-refused`, The destination is refused; `model-work-refused`, Model work is refused by the request; `cost-exceeds-cap`, The cost cap is below the smallest call; `version-withdrawn`, The version is no longer served; `idempotency-key-reused`, The idempotency key was reused with another body.
- 429 `rate-limit-exceeded`, The rate limit is exceeded; `concurrency-limit-exceeded`, Too many calls are in flight.
- 451 `legal-block`, Withheld under a legal demand.
- 500 `internal-error`, The service failed.
- 503 `overloaded`, The service is overloaded.

**When a record is not delivered.** `outcome.message` says what may work next, and the table under `Outcome.reason` gives it for every reason.
</dd>
</dl>
</dd>
</dl>

#### Usage

<dl>
<dd>

<dl>
<dd>

```python
from getclean import GetClean
from getclean.environment import GetCleanEnvironment

client = GetClean(
    environment=GetCleanEnvironment.PRODUCTION,
)

client.fetch_contents(
    url="https://example.com/q3",
    highlights=[
        "Revenue rose 12%",
        "what drove the margin"
    ],
    summary=True,
)

```
</dd>
</dl>
</dd>
</dl>

#### Parameters

<dl>
<dd>

<dl>
<dd>

**url:** `str` — The address to fetch, a page or a document; getclean tells which. Required. http or https, at most 2,048 characters. A scheme other than http or https, or a password in the URL's userinfo, is refused `invalid-field`, `syntax`; localhost, an address that is not globally reachable or a bad port is `destination-refused`; a host outside the key's domain policy is `policy-limit-exceeded`.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `typing.Optional[str]` 

One key per logical call, so a retry is never billed twice.

Optional on this operation; required on `upload_contents`, `fetch_contents_batch` and `search_batch`, where a duplicate would cost the most. The SDKs fill a fresh key when you give none and send the same key on every retry of that call. Give your own key when your program retries across processes, so the second run finds the first answer.

The form: 1 to 255 visible ASCII characters, used exactly as sent, so a value written as a quoted Structured Field String keeps its quotes as part of the key. That is a stated departure from the IETF draft `draft-ietf-httpapi-idempotency-key-header`, revision 08, which is not yet a standard; this parameter documents the form in full.

What a repeated key does:
- The same key with the same body returns the first answer again, with this call's `request_id`, `expires_at` as it stands and `replayed` true on every `cost`. Nothing is billed again.
- The same key while the first call still runs: `409 idempotency-key-in-flight`, with `Retry-After`.
- The same key with another body: `422 idempotency-key-reused`.

Answers are stored for 24 hours, per account, for billed answers and running jobs only; a free answer is not stored. A call that may bill is kept in the store from its start, so a second call with its key meets the `409` while it runs.
    
</dd>
</dl>

<dl>
<dd>

**max_characters:** `typing.Optional[int]` — The most text to return, in characters. `0` returns no text but the map of sections and the facts, which is how you see a document's size before paying for its text. Default 20,000; `0`, or 1,000 to 1,000,000; a value between 1 and 999 is refused `bound`.
    
</dd>
</dl>

<dl>
<dd>

**scope:** `typing.Optional[Scope]` — Which view to return: `main`, the main content alone, or `whole_page`, everything on the page. Default `main`. A document has one view, so `whole_page` on a document makes the notice `field_not_applicable`.
    
</dd>
</dl>

<dl>
<dd>

**formats:** `typing.Optional[typing.Sequence[str]]` — The formats to return, 0 to 7 of these: `markdown`, the content as one markdown string; `html`, as clean HTML; `doclang`, as DocLang, an XML that keeps each block with its place on the page; `json`, as `Block` objects; `links`, every link with its kind; `screenshot`, a picture of the whole page; `raw_html`, the page's bytes exactly as served. `[]` returns the facts only. Default `["markdown"]`. An open set; a repeated value is refused `duplicate`, a value outside the set `not_allowed`. `doclang`, `screenshot` and `raw_html` apply to a web page only; on a document each makes the notice `field_not_applicable`.
    
</dd>
</dl>

<dl>
<dd>

**block_kinds:** `typing.Optional[typing.Sequence[str]]` — Keep only blocks of these kinds, in every format and in every model step: 1 to 10 of `text`, `heading`, `code`, `math`, `divider`, `interactive`, `table`, `image`, `embed`, `media`, an open set. Default: every kind. An empty list is refused `bound`. When nothing would use it, no text format, no `links`, no `highlights`, no `json_schema` and no `summary`, the notice `field_not_applicable` says so.
    
</dd>
</dl>

<dl>
<dd>

**highlights:** `typing.Optional[typing.Sequence[str]]` — Words or questions to find in the content and mark where they stand, 1 to 5 strings of 1 to 4,000 characters each. Each string is one query, and every place it finds carries its position as `query_index`. Default none. Sending this without `deterministic_only` needs `contents:model`, since a string may need a model. A string found verbatim costs nothing; the strings a model had to judge cost one model step for the whole call.
    
</dd>
</dl>

<dl>
<dd>

**json_schema:** `typing.Optional[typing.Dict[str, typing.Any]]` — Your own fields, filled from the content by a model, each value with the words it came from; one model step, needs `contents:model`. A JSON Schema 2020-12 object whose root is `type: object` with `properties`, at most 50 KB. Default none. A schema that is not valid JSON Schema is refused `syntax`; one whose root is not `type: object`, that has no `properties`, or whose `pattern` needs backtracking is refused `not_allowed`. Under the request's `deterministic_only` it is refused `model-work-refused`; under a key whose policy forbids model work, `policy-limit-exceeded`.
    
</dd>
</dl>

<dl>
<dd>

**summary:** `typing.Optional[bool]` — Have a model write a summary of the content, at most 1,500 characters, in the content's language; one model step, needs `contents:model`. Default false. Under the request's `deterministic_only` it is refused `model-work-refused`; under a key whose policy forbids model work, `policy-limit-exceeded`.
    
</dd>
</dl>

<dl>
<dd>

**deterministic_only:** `typing.Optional[bool]` — Turn off every step whose output could differ between two runs of the same input: no judged highlight, no schema fill, no summary, and the publisher's kind only from what getclean already knows. The text and the ids repeat on every call of the same input under one version in any case; with this on, every other part of the answer repeats too, but for what belongs to the call itself: `request_id`, `fetched_at`, `expires_at`, `elapsed_seconds` and `cost`. Text recognition on a scanned page still runs and is listed, since it repeats under one version. Default false. A key whose policy forbids model work makes it true, with the notice `default_set_by_policy`; sending false under such a key is `policy-limit-exceeded`.
    
</dd>
</dl>

<dl>
<dd>

**baseline_fingerprint:** `typing.Optional[str]` — The fingerprint of a copy you already hold, as a record returned it. When the page still matches it, the answer is `unchanged` with no text, at the fetch's price, and you know nothing moved. Default none. A malformed value is refused `syntax`. A fingerprint no record of your account issued makes the notice `fingerprint_unknown`, and one issued under another scope, version, configuration or kind of source the notice `fingerprint_incomparable`; in both cases the fetch runs whole.
    
</dd>
</dl>

<dl>
<dd>

**as_of_date:** `typing.Optional[datetime.date]` — Read the page as an archive kept it on that day: the latest capture at or before the end of the day, UTC. A date not after today in UTC. Default none, the live page. On an archive copy, `subject_country`, `subject_language`, `screenshot` and `max_source_price` do not apply, a notice each.
    
</dd>
</dl>

<dl>
<dd>

**subject_country:** `typing.Optional[str]` — The country the page is read from, ISO 3166-1 alpha-2, one of the countries getclean can read from, `Limits.exits`. Default the key's `default_exit`. A country getclean cannot read from is refused `not_allowed`, with the countries it can read from in `allowed_values`. On a live page or a document at a URL only.
    
</dd>
</dl>

<dl>
<dd>

**subject_language:** `typing.Optional[str]` — The language to ask the site for, as its `Accept-Language`, a BCP 47 tag of 1 to 35 characters. Default none: getclean sends its usual `Accept-Language`, which `source.visitor.language` reports. On a live page or a document at a URL only.
    
</dd>
</dl>

<dl>
<dd>

**recognition_languages:** `typing.Optional[typing.Sequence[str]]` — The languages to expect on scanned pages, 1 to 10 BCP 47 tags of 1 to 35 characters each, among `Limits.recognition_languages`; another is refused `not_allowed`. Default detected: the document's declared language, else the language of its text, else the script found on the page. On a document only; on a web page the notice `field_not_applicable` says so.
    
</dd>
</dl>

<dl>
<dd>

**wait_seconds:** `typing.Optional[float]` — The most seconds this call may work, the read of the page or the document, every model step and the screenshot inside, counted from the moment the work starts; time spent waiting to start is not counted. 5 to 90; default 30. What did not finish by then is cut in the published order with a notice, or the outcome says so.
    
</dd>
</dl>

<dl>
<dd>

**max_cost:** `typing.Optional[Money]` — The most this call may cost, in the account's currency, reserved at the start against the balance and the budgets. Default the key's cap on one call. A value below the smallest call's price is refused `cost-exceeds-cap`, with `minimum_cap`.
    
</dd>
</dl>

<dl>
<dd>

**max_source_price:** `typing.Optional[Money]` — The most you would allow getclean to pay a site that asks a price for the page. getclean pays no site, whatever the value: a page that asks a price ends `payment_required`, with the price in `cost.source_price`. Default none.
    
</dd>
</dl>

<dl>
<dd>

**retention:** `typing.Optional[Retention]` — How long the record is kept. `none` keeps nothing past this answer, so the screenshot and the raw HTML travel inline; `hold` keeps the record 48 hours after its last call, at most 30 days, and is allowed only under a `hold` policy, since a request never loosens the key. Default the key's `policy.retention`.
    
</dd>
</dl>

<dl>
<dd>

**pinned_version:** `typing.Optional[str]` — The version of getclean to run under, at most 64 characters; it fixes the read configuration and every model step's version with it, and `execution.version` equals it. Default the current version, `Limits.current_version`. A version not served, never or no longer, is `version-withdrawn`, with the versions served.
    
</dd>
</dl>

<dl>
<dd>

**run_id:** `typing.Optional[str]` — The run the record belongs to, an existing run of the key; a key has one run, `run_default`. Default the key's default run. An unknown run is refused `not_allowed`.
    
</dd>
</dl>

<dl>
<dd>

**metadata:** `typing.Optional[typing.Dict[str, str]]` — Your own labels, returned on the record as sent and never passed to a site: at most 20 string pairs, keys of 1 to 64 characters, values of 1 to 512. Default none. An empty map is refused `bound`.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/getclean/client.py">get_contents</a>(...) -> Contents</code></summary>
<dl>
<dd>

#### Description

<dl>
<dd>

<dl>
<dd>

Read a record you already have, free: the same copy in any format, at any size, under either view, with the model work the fetch made.

Give it the `cnt_` id an earlier `fetch_contents`, `upload_contents` or `search` returned. Nothing is fetched from the web; the answer comes from the copy getclean kept. Use `fetch_contents` for a URL; use `get_section`, `list_blocks` and `list_links` to read one part of the record at a time.

**What it costs.** The key needs `contents:read`. The call is free, so the record carries no `cost` on this answer.

**What comes back.** `200` with `Contents`. The call moves the record's `expires_at` 48 hours ahead, never past 30 days from the record's making.
- The record's facts come as stored: `outcome`, `fetched_at`, `fingerprint`, `record_scope`, `source`, `pages`, `execution`, `retention`, `screenshot`, `raw_html`, and the fetch's `highlights`, `summary`, `schema_values` and `schema_statuses`.
- This answer's own: `scope`, the view delivered; `truncated`; `formats`; its notices after the record's own; `request_id`; `expires_at`.
- Under the record's own view, `counts`, `hidden_text` and `left_out` are the record's as stored; under the other view they describe that view.
- The text fits or does not fit under this call's `max_characters` as `fetch_contents` says; `truncated` says which. The record's `outcome` is never rewritten.
- The model work the fetch made comes back free, the marks placed where a highlighted block appears in the text returned. A new question is a call to `highlight_contents`, `fill_schema` or `summarize_contents`.
- `scope: whole_page` on a record fetched under `main` gives the whole page from the same read, free. The `fingerprint` stays that of `record_scope`; `counts` cover the page and `left_out` is `[]`; the section and block ids are the whole-page view's, and the fetch's highlights carry that view's ids. A document has one view, so `whole_page` on a document record makes the notice `field_not_applicable`.
- A record without content, failed, refused or needs a person, comes back as stored; the query's parameters make no notice, since nothing was asked of the text. An `unchanged` record keeps its content and is answered.
- `doclang` on a document that is not HTML is left out with the notice `field_not_applicable`.

**Refused before any work.**
- A value outside its set, `max_characters` between 1 and 999, a duplicate or an empty list: `400 invalid-request`, `not_allowed`, `bound` or `duplicate`, each with where it is.
- An id of the wrong kind: `400 invalid-request`, before any lookup.
- An unknown query parameter: `400 invalid-request`, `unknown_field`.

**Notices this operation makes.** `sections_cut`, `links_cut`, `field_not_applicable`, `version_retiring`, after the record's own notices.

**Problem types.**
- 400 `invalid-request`, The request is invalid.
- 401 `unauthorized`, The key is missing or rejected.
- 403 `insufficient-scope`, The key lacks a scope this call needs.
- 404 `not-found`, Not found: an unknown or another account's record.
- 410 `contents-expired`, The record has expired: for 30 days after it expired, to the owning account only, with `expired_at` and `change` naming `fetch_contents` and `url`; then `404`.
- 429 `rate-limit-exceeded`, The rate limit is exceeded; `concurrency-limit-exceeded`, Too many calls are in flight.
- 500 `internal-error`, The service failed.
- 503 `overloaded`, The service is overloaded.
</dd>
</dl>
</dd>
</dl>

#### Usage

<dl>
<dd>

<dl>
<dd>

```python
from getclean import GetClean
from getclean.environment import GetCleanEnvironment

client = GetClean(
    environment=GetCleanEnvironment.PRODUCTION,
)

client.get_contents(
    contents_id="cnt_5Gh7cdyeVQ6qoJhBFE31L1",
    max_characters=200000,
    formats=[
        "markdown"
    ],
)

```
</dd>
</dl>
</dd>
</dl>

#### Parameters

<dl>
<dd>

<dl>
<dd>

**contents_id:** `str` — The record to read, a `cnt_` id as `fetch_contents`, `upload_contents` or `search` returned it.
    
</dd>
</dl>

<dl>
<dd>

**max_characters:** `typing.Optional[int]` — The most text to return, in characters. `0` returns no text but the map of sections and the facts. Default 20,000; `0`, or 1,000 to 1,000,000; a value between 1 and 999 is refused `bound`.
    
</dd>
</dl>

<dl>
<dd>

**scope:** `typing.Optional[Scope]` — Which view to return: `main`, the main content alone, or `whole_page`, everything on the page from the same read. Default the record's own view, `record_scope`. A document has one view, so `whole_page` on a document record makes the notice `field_not_applicable`.
    
</dd>
</dl>

<dl>
<dd>

**formats:** `typing.Optional[typing.Union[str, typing.Sequence[str]]]` — The formats to return, 1 to 5 of these, one value per repeated key: `markdown`, the content as one markdown string; `html`, as clean HTML; `doclang`, as DocLang, an XML that keeps each block with its place on the page, on a page or an HTML file only; `json`, as `Block` objects; `links`, every link with its kind. Default `markdown`. `screenshot` and `raw_html` are not values here; the ones the fetch made come with every answer. An open set; a key sent with an empty value is an empty list, refused `bound`, and a repeated value is refused `duplicate`.
    
</dd>
</dl>

<dl>
<dd>

**block_kinds:** `typing.Optional[typing.Union[str, typing.Sequence[str]]]` — Keep only blocks of these kinds, in every format: 1 to 10 of `text`, `heading`, `code`, `math`, `divider`, `interactive`, `table`, `image`, `embed`, `media`, an open set, one value per repeated key. Default: every kind.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/getclean/client.py">delete_contents</a>(...)</code></summary>
<dl>
<dd>

#### Description

<dl>
<dd>

<dl>
<dd>

Erase a record before it expires: the record, its screenshot, its raw HTML, its document images, its recognized page images and its stored replays. Later calls on the id answer `404`. A retry of the fetch with its idempotency key, within the key's 24 hours, answers `404` naming the deletion, never a second fetch. A job that points at the record keeps its `contents_id`, and that id answers `404`. A second delete is `404`.

**What it costs.** The key needs `contents:delete`. The call is free. The answer is `204 No Content`.

**Refused before any work.** An id of the wrong kind: `400 invalid-request`, before any lookup. An unknown query parameter: `400 invalid-request`, `unknown_field`.

**Problem types.**
- 400 `invalid-request`, The request is invalid.
- 401 `unauthorized`, The key is missing or rejected.
- 403 `insufficient-scope`, The key lacks a scope this call needs.
- 404 `not-found`, Not found: an unknown or another account's record, or one already erased.
- 410 `contents-expired`, The record has expired: for 30 days after it expired, to the owning account only; then `404`.
- 429 `rate-limit-exceeded`, The rate limit is exceeded; `concurrency-limit-exceeded`, Too many calls are in flight.
- 500 `internal-error`, The service failed.
- 503 `overloaded`, The service is overloaded.
</dd>
</dl>
</dd>
</dl>

#### Usage

<dl>
<dd>

<dl>
<dd>

```python
from getclean import GetClean
from getclean.environment import GetCleanEnvironment

client = GetClean(
    environment=GetCleanEnvironment.PRODUCTION,
)

client.delete_contents(
    contents_id="cnt_3Fk9abaUhNX7t2eKkgfd3e",
)

```
</dd>
</dl>
</dd>
</dl>

#### Parameters

<dl>
<dd>

<dl>
<dd>

**contents_id:** `str` — The record to erase, a `cnt_` id.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/getclean/client.py">get_section</a>(...) -> SectionContents</code></summary>
<dl>
<dd>

#### Description

<dl>
<dd>

<dl>
<dd>

Read one section of a record, free: its text when it fits, its own text and the rows of its child sections when it does not, and a page of its text when a cut is needed.

Give it the record's `cnt_` id and the section's `s` id from the map, `sections`, which a fetch returns when the text did not fit or when `max_characters` was `0`. `s0` is the text before the first heading; on a page or a document without headings it is the whole text. Use `get_contents` for the whole record; use `list_blocks` for the blocks of a section by kind.

**What it costs.** The key needs `contents:read`. The call is free.

**What comes back.** `200` with `SectionContents`: first the record's id, address, fetch time, fingerprint, version and configuration, then its new `expires_at`, then the section's row, then its text in the formats asked for, or its child rows.
- The section fits `max_characters`: its text comes whole in the formats asked; `truncated` is false; no `sections`.
- It does not fit and has child sections: its own text before the first child comes, with `sections`, the child rows, on this first page only; `truncated` is true; no `next_page_token`, since each child is read by its own id.
- It does not fit and has no children, or its own text alone does not fit: the text is cut at a block edge; `truncated` is true; `next_page_token` continues it.
- One block larger than the bound: the text is cut inside the block, at a row, an item, a line or a sentence edge; `truncated` is true; `next_page_token` continues it.
- `max_characters: 0`: the row and the child rows, no text; `truncated` is false.
- `links` are the section's links, narrowed by `block_kinds`; they come under `0` too.
- The token binds the other parameters; a change is `400 page-token-invalid`. It is alive as long as the record, and a page that carries `next_page_token` always has text.

**Refused before any work.**
- A value outside its set, `max_characters` between 1 and 999, a duplicate or an empty list: `400 invalid-request`, `not_allowed`, `bound` or `duplicate`, each with where it is.
- An id of the wrong kind: `400 invalid-request`, before any lookup.
- A token of another record, another section or another query: `400 page-token-invalid`.
- A record that failed, was refused or needs a person: `409 record-without-content`, `change` naming `fetch_contents`.
- An unknown query parameter: `400 invalid-request`, `unknown_field`.

**Notices this operation makes.** `sections_cut`, `links_cut`, `field_not_applicable`, `version_retiring`, after the record's own notices.

**Problem types.**
- 400 `invalid-request`, The request is invalid; `page-token-invalid`, The page token is invalid.
- 401 `unauthorized`, The key is missing or rejected.
- 403 `insufficient-scope`, The key lacks a scope this call needs.
- 404 `not-found`, Not found, `change.field` saying `contents_id` or `section_id`.
- 409 `record-without-content`, The record has no content.
- 410 `contents-expired`, The record has expired.
- 429 `rate-limit-exceeded`, The rate limit is exceeded; `concurrency-limit-exceeded`, Too many calls are in flight.
- 500 `internal-error`, The service failed.
- 503 `overloaded`, The service is overloaded.
</dd>
</dl>
</dd>
</dl>

#### Usage

<dl>
<dd>

<dl>
<dd>

```python
from getclean import GetClean
from getclean.environment import GetCleanEnvironment

client = GetClean(
    environment=GetCleanEnvironment.PRODUCTION,
)

client.get_section(
    contents_id="cnt_3Fk9abaUhNX7t2eKkgfd3e",
    section_id="s2",
    formats=[
        "markdown"
    ],
)

```
</dd>
</dl>
</dd>
</dl>

#### Parameters

<dl>
<dd>

<dl>
<dd>

**contents_id:** `str` — The record, a `cnt_` id.
    
</dd>
</dl>

<dl>
<dd>

**section_id:** `str` — The section, an `s` id of the view asked, as the map's rows name it; `s0` is the text before the first heading.
    
</dd>
</dl>

<dl>
<dd>

**max_characters:** `typing.Optional[int]` — The most text to return, in characters. `0` returns the section's row and its child rows, no text. Default 20,000; `0`, or 1,000 to 1,000,000; a value between 1 and 999 is refused `bound`.
    
</dd>
</dl>

<dl>
<dd>

**scope:** `typing.Optional[Scope]` — Which view's ids and text: `main` or `whole_page`. Default the record's own.
    
</dd>
</dl>

<dl>
<dd>

**formats:** `typing.Optional[typing.Union[str, typing.Sequence[str]]]` — The formats to return, over this section, 1 to 5 of these, one value per repeated key: `markdown`, the text as one markdown string; `html`, as clean HTML; `doclang`, as DocLang, an XML that keeps each block with its place on the page, on a page or an HTML file only; `json`, as `Block` objects; `links`, the section's links with their kinds. Default `markdown`. An open set; a key sent with an empty value is an empty list, refused `bound`, and a repeated value is refused `duplicate`.
    
</dd>
</dl>

<dl>
<dd>

**block_kinds:** `typing.Optional[typing.Union[str, typing.Sequence[str]]]` — Keep only blocks of these kinds, over this section: 1 to 10 of `text`, `heading`, `code`, `math`, `divider`, `interactive`, `table`, `image`, `embed`, `media`, an open set, one value per repeated key. Default: every kind.
    
</dd>
</dl>

<dl>
<dd>

**page_token:** `typing.Optional[str]` — Continues a cut text, as the last answer's `next_page_token` gave it; opaque, at most 1,024 characters, alive as long as the record. Default none.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/getclean/client.py">list_blocks</a>(...) -> SyncPager[Block, BlockPage]</code></summary>
<dl>
<dd>

#### Description

<dl>
<dd>

<dl>
<dd>

List the blocks of a record, free: by kind, by section, by document page or by id, in document order, one page of results at a time.

Give it the record's `cnt_` id and the filters you want; every filter you send must match. Each block is the record's own `Block`: its id, kind, section, size and text, a table as its rows and spans, an image as its address and size. `block_ids` reads the blocks a highlight names by `block_id`, so you can read the whole block around a match. Use `get_section` for a section's text in one piece; use `get_contents` for the whole record.

**What it costs.** The key needs `contents:read`. The call is free.

**What comes back.** `200` with `BlockPage`: the record's id and facts, the record's new `expires_at`, the blocks, and `next_page_token` while more remain.
- A page of results ends before the block that would pass `max_characters`, or at `page_size` blocks, whichever comes first.
- One block alone larger than `max_characters` comes whole, alone on its page, with the notice `block_over_limit`.
- `highlight_ids` is empty on every block here; the fetch's highlights stand on the record.
- No block matching: `200` with `[]`.
- `page_size` is from 1, default 50, maximum 200; a larger value is lowered with the notice `page_size_lowered`, never refused.
- `page_token` is bound to its query and its record and is alive as long as the record; `next_page_token` is absent on the last page, and a page that carries it has at least one block.

**Refused before any work.**
- A value outside its set or range, a duplicate or an empty list: `400 invalid-request`, `not_allowed`, `bound` or `duplicate`, each with where it is; `page_size` above its maximum is lowered instead.
- `page_number` on a record without `pages`: `400 invalid-request`, `dependent`; above `pages.count`: `400 invalid-request`, `bound`.
- `block_ids` with `start_block_id`: `400 invalid-request`, `exclusive`.
- An id of the wrong kind: `400 invalid-request`, before any lookup.
- A token of another record or another query: `400 page-token-invalid`.
- A `section_id`, a `block_ids` value or a `start_block_id` the record does not hold: `404 not-found`, `change.field` naming it.
- A record that failed, was refused or needs a person: `409 record-without-content`.
- An unknown query parameter: `400 invalid-request`, `unknown_field`.

**Notices this operation makes.** `block_over_limit`, `page_size_lowered`, `field_not_applicable`, `version_retiring`, after the record's own notices.

**Problem types.**
- 400 `invalid-request`, The request is invalid; `page-token-invalid`, The page token is invalid.
- 401 `unauthorized`, The key is missing or rejected.
- 403 `insufficient-scope`, The key lacks a scope this call needs.
- 404 `not-found`, Not found, `change.field` saying `contents_id`, `section_id`, `block_ids` or `start_block_id`.
- 409 `record-without-content`, The record has no content.
- 410 `contents-expired`, The record has expired.
- 429 `rate-limit-exceeded`, The rate limit is exceeded; `concurrency-limit-exceeded`, Too many calls are in flight.
- 500 `internal-error`, The service failed.
- 503 `overloaded`, The service is overloaded.
</dd>
</dl>
</dd>
</dl>

#### Usage

<dl>
<dd>

<dl>
<dd>

```python
from getclean import GetClean
from getclean.environment import GetCleanEnvironment

client = GetClean(
    environment=GetCleanEnvironment.PRODUCTION,
)

client.list_blocks(
    contents_id="cnt_3Fk9abaUhNX7t2eKkgfd3e",
    block_kinds=[
        "table"
    ],
    section_id="s2",
    block_ids=[
        "b7"
    ],
)

```
</dd>
</dl>
</dd>
</dl>

#### Parameters

<dl>
<dd>

<dl>
<dd>

**contents_id:** `str` — The record, a `cnt_` id.
    
</dd>
</dl>

<dl>
<dd>

**block_kinds:** `typing.Optional[typing.Union[str, typing.Sequence[str]]]` — Keep only blocks of these kinds: 1 to 10 of `text`, `heading`, `code`, `math`, `divider`, `interactive`, `table`, `image`, `embed`, `media`, an open set, one value per repeated key. Default: every kind.
    
</dd>
</dl>

<dl>
<dd>

**section_id:** `typing.Optional[str]` — Keep only the blocks of this section and of the sections under it, an `s` id from the map. Default none.
    
</dd>
</dl>

<dl>
<dd>

**page_number:** `typing.Optional[int]` — Keep only the blocks of this page of a document, from 1 to `pages.count`. Default none. On a record without `pages`, a web page, it is refused `dependent`; above `pages.count`, `bound`.
    
</dd>
</dl>

<dl>
<dd>

**block_ids:** `typing.Optional[typing.Union[str, typing.Sequence[str]]]` — Keep only these blocks, 1 to 50 `b` ids, one value per repeated key; the ids a highlight names. Default none. With `start_block_id` it is refused `exclusive`.
    
</dd>
</dl>

<dl>
<dd>

**start_block_id:** `typing.Optional[str]` — Begin the page of results at this block, a `b` id, and read on from there in document order. Default none, the first block. With `block_ids` it is refused `exclusive`.
    
</dd>
</dl>

<dl>
<dd>

**scope:** `typing.Optional[Scope]` — Which view's blocks: `main` or `whole_page`. Default the record's own.
    
</dd>
</dl>

<dl>
<dd>

**max_characters:** `typing.Optional[int]` — The most text on one page of results, in characters; the page ends before the block that would pass it. Default 20,000; 1,000 to 1,000,000.
    
</dd>
</dl>

<dl>
<dd>

**page_size:** `typing.Optional[int]` — At most this many blocks on a page of results, from 1. Default 50; the maximum, 200, stands in `Limits.bounds`, and a larger value is lowered with the notice `page_size_lowered`.
    
</dd>
</dl>

<dl>
<dd>

**page_token:** `typing.Optional[str]` — The next page, as the last answer's `next_page_token` gave it; opaque, at most 1,024 characters, alive as long as the record. Default none, the first page.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/getclean/client.py">list_links</a>(...) -> SyncPager[Link, LinkPage]</code></summary>
<dl>
<dd>

#### Description

<dl>
<dd>

<dl>
<dd>

List the links of a record, free: every link with its kind and the block and section that hold it, in document order, one page of results at a time, without the 1,000-link cap a fetch puts on `formats: links`.

Give it the record's `cnt_` id and the filters you want; every filter you send must match. Use `fetch_contents` to read a linked page; use `list_blocks` for the blocks themselves.

**What it costs.** The key needs `contents:read`. The call is free.

**What comes back.** `200` with `LinkPage`: the record's id and facts, the record's new `expires_at`, the links, each with its kind and its place, and `next_page_token` while more remain.
- The order is the document order of the blocks that hold the links.
- `kind` is read from the address alone, a guess: no request is made for any link, so a link carries no size and no served type.
- `external` compares the link's host with the final URL's registrable domain; a link without a host, `mail`, `phone` or `fragment`, is left out under either value of the filter.
- No link matching: `200` with `[]`.
- `page_size` is from 1, default 50, maximum 200; a larger value is lowered with the notice `page_size_lowered`, never refused.
- `page_token` is bound to its query and its record and is alive as long as the record; `next_page_token` is absent on the last page, and a page that carries it has at least one link.

**Refused before any work.**
- A value outside its set or range, a duplicate or an empty list: `400 invalid-request`, `not_allowed`, `bound` or `duplicate`, each with where it is; `page_size` above its maximum is lowered instead.
- An id of the wrong kind: `400 invalid-request`, before any lookup.
- A token of another record or another query: `400 page-token-invalid`.
- A `section_id` the record does not hold: `404 not-found`, `change.field` naming it.
- A record that failed, was refused or needs a person: `409 record-without-content`.
- An unknown query parameter: `400 invalid-request`, `unknown_field`.

**Notices this operation makes.** `page_size_lowered`, `field_not_applicable`, `version_retiring`, after the record's own notices.

**Problem types.**
- 400 `invalid-request`, The request is invalid; `page-token-invalid`, The page token is invalid.
- 401 `unauthorized`, The key is missing or rejected.
- 403 `insufficient-scope`, The key lacks a scope this call needs.
- 404 `not-found`, Not found, `change.field` saying `contents_id` or `section_id`.
- 409 `record-without-content`, The record has no content.
- 410 `contents-expired`, The record has expired.
- 429 `rate-limit-exceeded`, The rate limit is exceeded; `concurrency-limit-exceeded`, Too many calls are in flight.
- 500 `internal-error`, The service failed.
- 503 `overloaded`, The service is overloaded.
</dd>
</dl>
</dd>
</dl>

#### Usage

<dl>
<dd>

<dl>
<dd>

```python
from getclean import GetClean
from getclean.environment import GetCleanEnvironment

client = GetClean(
    environment=GetCleanEnvironment.PRODUCTION,
)

client.list_links(
    contents_id="cnt_3Fk9abaUhNX7t2eKkgfd3e",
    link_kinds=[
        "file"
    ],
    section_id="s3",
)

```
</dd>
</dl>
</dd>
</dl>

#### Parameters

<dl>
<dd>

<dl>
<dd>

**contents_id:** `str` — The record, a `cnt_` id.
    
</dd>
</dl>

<dl>
<dd>

**link_kinds:** `typing.Optional[typing.Union[str, typing.Sequence[str]]]` — Keep only links of these kinds: 1 to 7 of `file`, a file such as a PDF; `page`, another page; `fragment`, a place inside the same page; `mail`, an email address; `phone`, a phone number; `feed`, an RSS or Atom feed; `other`, anything else. An open set, one value per repeated key. Default: every kind.
    
</dd>
</dl>

<dl>
<dd>

**external:** `typing.Optional[bool]` — `true` keeps only links that leave the final URL's registrable domain; `false`, only those that stay. Default none, both. A link without a host is left out under either value.
    
</dd>
</dl>

<dl>
<dd>

**section_id:** `typing.Optional[str]` — Keep only the links of this section and of the sections under it, an `s` id from the map. Default none.
    
</dd>
</dl>

<dl>
<dd>

**scope:** `typing.Optional[Scope]` — Which view's links: `main` or `whole_page`. Default the record's own.
    
</dd>
</dl>

<dl>
<dd>

**page_size:** `typing.Optional[int]` — At most this many links on a page of results, from 1. Default 50; the maximum, 200, stands in `Limits.bounds`, and a larger value is lowered with the notice `page_size_lowered`.
    
</dd>
</dl>

<dl>
<dd>

**page_token:** `typing.Optional[str]` — The next page, as the last answer's `next_page_token` gave it; opaque, at most 1,024 characters, alive as long as the record. Default none, the first page.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/getclean/client.py">upload_contents</a>(...) -> ContentsUpload</code></summary>
<dl>
<dd>

#### Description

<dl>
<dd>

<dl>
<dd>

Read a document you hold, or one at a URL that needs more time than a fetch gives. You get the same record a fetch makes, the content with its structure intact, the map of its sections, the facts of the source, a fingerprint and the price, with `pages` saying how many pages were read, which failed and which were recognized from their image, and the record is kept for later reads.

Send the file as the `document` part, or its address as `url`. The parse runs on as a job when it needs more than `wait_seconds`: a scanned document takes seconds per page, and stopping early would lose pages, so this call may answer with a job where `fetch_contents` never does. Use `fetch_contents` for a web page, or for a document at a URL that fits in one wait; use `get_contents` to read a record you already have.

**What it costs.** The key needs `contents:fetch`, plus `contents:model` when you send `json_schema`, set `summary` or send `highlights` without `deterministic_only`; getclean decides this from the form before any work. The price is 1 `contents`, plus `document_pages` for every page parsed and `recognized_pages` for every page recognized, plus `model_steps` for each model field that ran. A long scan is the most expensive call there is, since each recognized page bills both page units. It is billed when the record becomes final: in the call that answered `201`, or when the job completes or is canceled with pages done. An `unchanged` answer bills the same 1 `contents`. A parse that failed, was refused or needs a person bills nothing.

**What comes back.**
- The parse finished within `wait_seconds`: `201 Created`, `Location` naming the record, and `ContentsUpload` with `contents` set, the record with its `cost`.
- The parse goes on: `202 Accepted`, `Location` naming the job, `Retry-After` saying when to read it, and `ContentsUpload` with `job` set. `get_job` reads the job, and `get_contents` reads the record once `contents_id` is set.
- The record is kept 48 hours after its last call and at most 30 days; the job is kept 30 days after its end.

**The body.** `multipart/form-data`, at most 101 MiB, the `document` part at most 100 MiB. Every field is a part under its own name.
- One of `document` and `url` is required; both at once is refused `exclusive`, neither `required`.
- A boolean is the text `true` or `false`; a number is decimal text.
- `json_schema`, `max_cost`, `max_source_price` and `metadata` are JSON parts, read as JSON whatever `Content-Type` the part declares.
- A list field is one part per value under the field's name.
- An empty value of a scalar field means the same as leaving it out; an empty value of a list field is an empty list, refused `bound`. Null cannot be written in a form.
- A scalar field sent as two parts is refused `duplicate`. A JSON part that does not parse is `422 invalid-field`, `syntax`, place `form`.
- The `document` part's `filename` and `Content-Type` are hints. The bytes decide the type, among `Limits.document_media_types`; where the bytes alone cannot tell, the declared type decides, then the extension, then plain text.
- `Expect: 100-continue` is honored. A declared `Content-Length` past 101 MiB, and every refusal the method, the path and the headers decide, `401`, `403 insufficient-scope` for `contents:fetch`, the `400` for a missing `Idempotency-Key`, `415` and `409 idempotency-key-in-flight`, is answered before `100 Continue`. The scope a form field decides, `contents:model`, is checked once the form is read and before any work. The `document` part's 100 MiB is checked as the part arrives, `413`.

**The idempotency key.** `Idempotency-Key` is required here, since a repeated upload would parse and bill the same document twice; without it the call is `400 invalid-request` naming the header. The same key with the same file and fields returns the first answer again, with this call's `request_id`, `expires_at` as it stands and `replayed` true on `cost`; nothing is billed again. The body is compared by its digest over the file and the fields. A retried start with the same key is the same job. The same key while the first call still runs is `409 idempotency-key-in-flight`; the same key with another body is `422 idempotency-key-reused`. A replay whose record was deleted is `404 not-found` naming the deletion.

**What comes back from a document.**
- Sections come from the document's own structure; a PDF without one, from its outline, else one row per page; a scan, one row per page. `Section.basis` says which.
- Blocks are `text`, `heading` and `table` where the format carries structure; `image` for an embedded image, served at its `url` with its digest; `math` where the format carries equations; `code` for a source file, one block per file, `code_language` from the extension. The other kinds occur only in an HTML file, which takes a page's kinds.
- `page_number` and `page_label` stand on every block of a paged format and on none of an unpaged one. `pages` is present for every document; on an unpaged format its `count` is the text's size in units of `bounds.contents.document_page_characters` characters, rounded up. A slide is a page.
- XML, JSON and YAML keep every key or element name, one `name: value` line per leaf, the top-level members as sections and the nested ones as headings.
- A spreadsheet's cells come as their stored displayed values under the workbook's locale, never another; each sheet is a section titled by its name, and its table carries `top_left_cell` and `formula_cells`.
- A DOCX keeps its bold, italics and strikethroughs; tracked changes are shown as accepted, with the notice `tracked_changes` and the count. A PDF keeps them only where it carries the structure for them; without it, the notice `marks_not_read` says so, and a strikethrough drawn as a line over text is not detected.
- A footnote reference stays as `[^n]`; the note's block carries `note_for` where the format links it; in a PDF without structure a footnote is a text block at the foot of its page.
- Tables come with their structure where the format carries it; a table that continues onto later pages is one block with `last_page_number`. The tables of a PDF without structure and of a scan come as text.
- Recognition runs on every page without a text layer. Each such page stands in `pages.recognized` with its confidence and a picture of the page; `execution.models` lists the step `recognition` with its version, and `language_detection` when the languages were detected; a page that yields no word stands in `failed_pages`; a recognized block carries `confidence`. A recognized page bills one `document_pages` unit and one `recognized_pages` unit. Handwriting and formulas without equation structure come as flattened text or not at all, with no notice.
- `highlights` on recognized text match the recognized words; `near` forgives case and end punctuation, and neither `exact` nor `near` forgives a recognition error.
- A still image sent as the document, PNG, JPEG, TIFF, WebP or HEIC, is one page without a text layer and is recognized like a scan. A compressed file such as a ZIP, a mailbox file, a saved web archive, an audio or a video file is refused as the record's outcome `unsupported_media_type`.
- The model steps, the highlight marks, the map's bound and `block_kinds` work as on `fetch_contents`, over the document's content.
- An HTML file is read as a page, from its bytes alone: nothing is fetched and nothing is run, so the styles, scripts and images it only points to are not loaded and its main content may differ from what the person saw. `main`, `left_out`, `hidden_text`, the walls and `sign_in_needed` apply to it; no screenshot is made.
- The fingerprint is the sha-256 over the markdown written from the document's blocks. `source.document_digest` is the sha-256 of the bytes, so you can check that the document parsed is the one you hold.
- On a file sent as `document`, `source` carries `url` as `captured_url` or not at all; no `final_url` and no `status_code`; `redirects` `[]`; `carrier` `upload`; no `access_kind`; `filename` as sent; `media_type` as the bytes showed it; `title`, `authors`, the dates and `language` as the document's properties declare them; no `publisher`, `canonical_url` or `archive`; `robots` `not_applicable`; no `visitor`. `scope` is `main`, the whole document; `hidden_text` and `left_out` are absent, present on an HTML file. The table under `Contents` says which members each kind of source carries.
- The bytes you sent are deleted when the parse ends; only the record is kept.

**Fields that do not apply.** Each is a notice `field_not_applicable` naming the field, never a refusal: `doclang` on a document that is not HTML; `max_source_price` with `document`; `block_kinds` with nothing to narrow. `recognition_languages` with no page to recognize has no effect and makes no notice.

**`url`.** getclean downloads the document and parses it as an upload, as a job when the parse outlives `wait_seconds`. `source.carrier` is `web`, and `source.url` and `final_url` are set. The address and domain rules of `fetch_contents` apply. A download that fails takes the outcomes of a fetch: `not_found`, `access_denied`, `rate_limited`, `server_error`, `http_error`, or a network failure named as RFC 9209 names it. A download that is a web page, a challenge or a sign-in page among them, is a record `refused`, `unsupported_media_type`, with the message naming `fetch_contents`: this call reads documents, not pages, and a wall can be told from a page only by reading it as one.

**`baseline_fingerprint`.** The bytes are checked first: when a record of your account issued the fingerprint and the file's `document_digest` matches it, the answer is `unchanged` with no parse and no page billed, at this call's price. Otherwise the parse runs and bills its pages, and a content fingerprint that matches then answers `unchanged`. If no record of your account issued the fingerprint, you get the notice `fingerprint_unknown`, and the parse runs whole.

**Money and time.** `max_cost` is reserved at the start. The pages are parsed, and recognized, one by one in order, and every stop keeps the pages done: the parse stops before the page that would pass the ceiling, `partial`, `cost_capped`, or `budget_capped` under a run's or a key's budget. The job's own bound is 30 minutes; past it the record ends `partial`, `time_capped`. `max_source_price` applies with `url` as on a fetch.

**The job.** It starts with `202`, `Location`, `Retry-After` and the job in the body, stored before the answer is sent.
- `completed`: `contents_id` is set and the record is delivered or partial.
- `failed`: `problem` is set when nothing was made; else `contents_id` is set and the record carries `failed`, `refused` or `needs_person`.
- `canceled` with pages done: a record `partial`, `canceled`, the pages kept and billed. With none: no record and nothing billed.
- `cost` is the units so far on every read, the final figure once `finished`.
- The job is kept 30 days after its end, then answers `410 job-expired` for 30 days to the owning account, then `404`. The record has its own life, 48 hours after its last call and at most 30 days, so a job may point at a record that has expired.

**Refused before any work**, every violation of the form reported at once in `violations`, place `form`:
- `Idempotency-Key` absent: `400 invalid-request`.
- A body that is not `multipart/form-data`, or carries a content coding: `415 unsupported-media-type`.
- `document` and `url` both present: `invalid-field`, `exclusive`; neither: `required`.
- `captured_url` or `captured_at` with `url`: `dependent`. `captured_url` with a scheme other than http or https, or `captured_at` that is not an RFC 3339 instant: `syntax`.
- `scope`, `as_of_date`, `subject_country` or `subject_language`, which belong to a page and not to a file: `unknown_field`.
- The `document` part over 100 MiB: `413 body-too-large`.
- Every rule of `fetch_contents` on the fields the two share, with the same kinds:
  - a `formats` value, a `block_kinds` value or `retention` outside its set: `not_allowed`; a duplicate value: `duplicate`;
  - `max_characters` between 1 and 999, or any other bound passed: `bound`;
  - `json_schema` or `summary` under `deterministic_only`: `model-work-refused`; `json_schema`, `summary` or `deterministic_only: false` under a key whose policy forbids model work: `403 policy-limit-exceeded`;
  - `max_cost` below the smallest call's price: `cost-exceeds-cap`;
  - a malformed `baseline_fingerprint`: `syntax`; a `json_schema` that is not valid JSON Schema: `syntax`, and one whose root is not `type: object`, that has no `properties`, or whose `pattern` needs backtracking: `not_allowed`;
  - an unknown `run_id`: `not_allowed`; `retention: hold` under a `none` policy: `403 policy-limit-exceeded`; an unknown field: `unknown_field`; `pinned_version` not served: `version-withdrawn`.
- With `url`: a scheme other than http or https, or a password in the userinfo, `syntax`; localhost, an address that is not globally reachable, or a bad port, `destination-refused`; a host outside the key's domain policy, or a URL the key's credential policy refuses, `403 policy-limit-exceeded`.

**Notices this operation makes.** `highlight_not_found`, `highlights_cut`, `sections_cut`, `links_cut`, `structured_data_cut`, `size_limit`, `conversion_mismatch`, `field_not_applicable`, `cost_cut`, `budget_cut`, `time_cut`, `step_failed`, `model_link_removed`, `recognition_uncertain`, `tracked_changes`, `fingerprint_incomparable`, `fingerprint_unknown`, `marks_not_read`, `default_set_by_policy`, `version_retiring`; on an HTML file also `hidden_text_cut`, `unread_region`, `no_main_content` and `paywall_declared`; with `url` also `redirected`. `content_not_rendered` is a published code that this version does not make.

**Problem types.**
- 400 `invalid-request`, The request is invalid.
- 401 `unauthorized`, The key is missing or rejected.
- 403 `insufficient-scope`, The key lacks a scope this call needs; `policy-limit-exceeded`, The key's policy forbids this; `credit-exhausted`, The credit is exhausted; `run-budget-exhausted`, The run's budget is exhausted; `key-budget-exhausted`, The key's budget is exhausted.
- 404 `not-found`, Not found, on a replay whose record was deleted.
- 409 `idempotency-key-in-flight`, The same request is still running.
- 413 `body-too-large`, The body is too large.
- 415 `unsupported-media-type`, The media type is not supported.
- 422 `invalid-field`, A field is invalid; `destination-refused`, The destination is refused, with `url`; `model-work-refused`, Model work is refused by the request; `cost-exceeds-cap`, The cost cap is below the smallest call; `version-withdrawn`, The version is no longer served; `idempotency-key-reused`, The idempotency key was reused with another body.
- 429 `rate-limit-exceeded`, The rate limit is exceeded; `concurrency-limit-exceeded`, Too many calls are in flight.
- 451 `legal-block`, Withheld under a legal demand.
- 500 `internal-error`, The service failed.
- 503 `overloaded`, The service is overloaded.

**When a record is not delivered.** `outcome.message` says what may work next, and the table under `Outcome.reason` gives it for every reason.
</dd>
</dl>
</dd>
</dl>

#### Usage

<dl>
<dd>

<dl>
<dd>

```python
from getclean import GetClean
from getclean.environment import GetCleanEnvironment

client = GetClean(
    environment=GetCleanEnvironment.PRODUCTION,
)

client.upload_contents(
    document="minutes.pdf",
)

```
</dd>
</dl>
</dd>
</dl>

#### Parameters

<dl>
<dd>

<dl>
<dd>

**idempotency_key:** `typing.Optional[str]` 

One key per logical call, so a retry is never billed twice.

Required on this operation, where a duplicate would cost the most; without it the call is `400 invalid-request` naming the header. The SDKs fill a fresh key when you give none and send the same key on every retry of that call. Give your own key when your program retries across processes, so the second run finds the first answer.

The form: 1 to 255 visible ASCII characters, used exactly as sent, so a value written as a quoted Structured Field String keeps its quotes as part of the key. That is a stated departure from the IETF draft `draft-ietf-httpapi-idempotency-key-header`, revision 08, which is not yet a standard; this parameter documents the form in full.

What a repeated key does:
- The same key with the same body returns the first answer again, with this call's `request_id`, the current `expires_at` and `replayed` true on every `cost`. Nothing is billed again. On the upload the body is compared by a digest over the document and the fields, and a retried start with the same key is the same job.
- The same key while the first call still runs: `409 idempotency-key-in-flight`, with `Retry-After`.
- The same key with another body: `422 idempotency-key-reused`.

Answers are stored for 24 hours, per account, for billed answers and running jobs only. A call that may bill is kept in the store from its start, so a second call with its key meets the `409` while it runs.
    
</dd>
</dl>

<dl>
<dd>

**document:** `typing.Optional[core.File]` — The file to read, as the one file part, at most 100 MiB, with any media type on the wire. The part's `filename` and `Content-Type` are hints only: the bytes decide the type, among `Limits.document_media_types`; where the bytes alone cannot tell, the declared type, then the extension, then plain text. A still image is read as one scanned page. A compressed file such as a ZIP, a mailbox file, a saved web archive, an audio or a video file is refused as the record's outcome `unsupported_media_type`. One of `document` and `url` is required.
    
</dd>
</dl>

<dl>
<dd>

**url:** `typing.Optional[str]` — Where the file is, http or https, at most 2,048 characters, under the same address and domain rules as a fetch. getclean downloads it and reads it as an upload, as a job when the reading outlives `wait_seconds`. A URL that serves a web page is a record `refused`, `unsupported_media_type`, with the message naming `fetch_contents`. One of `document` and `url` is required.
    
</dd>
</dl>

<dl>
<dd>

**captured_url:** `typing.Optional[str]` — The address the page you saved came from, when `document` is a page you captured yourself, as you state it; recorded as `source.url` with `carrier` `upload`, so the record says where the page was seen. http or https, at most 2,048 characters; a scheme other than http or https is refused `syntax`. With `document` only; with `url` it is refused `dependent`. Default none.
    
</dd>
</dl>

<dl>
<dd>

**captured_at:** `typing.Optional[datetime.datetime]` — When you saved the page, as you state it, an RFC 3339 instant, kept in UTC; recorded as `source.captured_at`. A value that is not an RFC 3339 instant is refused `syntax`. With `document` only; with `url` it is refused `dependent`. Default none.
    
</dd>
</dl>

<dl>
<dd>

**baseline_fingerprint:** `typing.Optional[str]` — The fingerprint of a copy you already hold, as a record returned it, `sha-256=:…:`. The bytes are checked first: when a record of this account issued the fingerprint and the file's `document_digest` matches it, the answer is `unchanged` with no parse and no page billed, at this call's price. Otherwise the parse runs and bills its pages, and a content fingerprint that matches then answers `unchanged`. Default none. A malformed value is refused `syntax`; a fingerprint no record of this account issued makes the notice `fingerprint_unknown`, and the parse runs whole.
    
</dd>
</dl>

<dl>
<dd>

**max_characters:** `typing.Optional[int]` — The most text to return, in characters. `0` returns no text but the map of sections and the facts, which is how you see a document's shape before reading its text. Default 20,000; `0`, or 1,000 to 1,000,000; a value between 1 and 999 is refused `bound`.
    
</dd>
</dl>

<dl>
<dd>

**formats:** `typing.Optional[typing.Sequence[str]]` — The formats to return, 1 to 5 of these, one part per value: `markdown`, the content as one markdown string; `html`, as clean HTML; `doclang`, as DocLang, an XML that keeps each block with its place on the page, on an HTML file only; `json`, as `Block` objects; `links`, every link with its kind. Default `["markdown"]`. A form has no part for an empty list, so a field left out takes its default and a part sent with an empty value is an empty list, refused `bound`; the map and the facts alone come by `max_characters: 0`. `screenshot` and `raw_html` are not values here, since an upload reads a file and never a live page. An open set; a repeated value is refused `duplicate`, a value outside the set `not_allowed`, and `doclang` on a document that is not HTML makes the notice `field_not_applicable`.
    
</dd>
</dl>

<dl>
<dd>

**block_kinds:** `typing.Optional[typing.Sequence[str]]` — Keep only blocks of these kinds, in every format and in every model step: 1 to 10 of `text`, `heading`, `code`, `math`, `divider`, `interactive`, `table`, `image`, `embed`, `media`, an open set, one part per value. Default: every kind. In a document only `text`, `heading`, `table`, `image`, `math` and `code` occur; an HTML file takes every kind. An empty list is refused `bound`, a repeated value `duplicate`. When nothing would use it, no text format, no `links`, no `highlights`, no `json_schema` and no `summary`, the notice `field_not_applicable` says so.
    
</dd>
</dl>

<dl>
<dd>

**highlights:** `typing.Optional[typing.Sequence[str]]` — Words or questions to find in the content and mark where they stand, as on `fetch_contents`: 1 to 5 strings of 1 to 4,000 characters each, one part per value. Each string is one query, and every place it finds carries its position as `query_index`. Default none. Sending this without `deterministic_only` needs `contents:model`, since a string may need a model. A string found verbatim costs nothing; the strings a model had to judge cost one model step for the whole call. On recognized text, `exact` and `near` match the recognized words; `near` forgives case and end punctuation, and neither forgives a recognition error.
    
</dd>
</dl>

<dl>
<dd>

**json_schema:** `typing.Optional[typing.Dict[str, typing.Any]]` — Your own fields, filled from the content by a model, each value with the words it came from; one model step, needs `contents:model`. A JSON part: a JSON Schema 2020-12 object whose root is `type: object` with `properties`, at most 50 KB. Default none. A schema that is not valid JSON Schema is refused `syntax`; one whose root is not `type: object`, that has no `properties`, or whose `pattern` needs backtracking is refused `not_allowed`. Under the request's `deterministic_only` it is refused `model-work-refused`; under a key whose policy forbids model work, `policy-limit-exceeded`.
    
</dd>
</dl>

<dl>
<dd>

**summary:** `typing.Optional[bool]` — Have a model write a summary of the content, at most 1,500 characters, in the content's language; one model step, needs `contents:model`. Default false. Under the request's `deterministic_only` it is refused `model-work-refused`; under a key whose policy forbids model work, `policy-limit-exceeded`.
    
</dd>
</dl>

<dl>
<dd>

**deterministic_only:** `typing.Optional[bool]` — Turn off every step whose output could differ between two runs of the same bytes: no judged highlight, no schema fill, no summary. The text and the ids repeat on every call of the same input under one version in any case; with this on, every other part of the answer repeats too, but for what belongs to the call itself: `request_id`, `fetched_at`, `expires_at`, `elapsed_seconds` and `cost`. Text recognition on a page without a text layer still runs and is listed, since it repeats under one version. Default false. A key whose policy forbids model work makes it true, with the notice `default_set_by_policy`; sending false under such a key is `policy-limit-exceeded`.
    
</dd>
</dl>

<dl>
<dd>

**recognition_languages:** `typing.Optional[typing.Sequence[str]]` — The languages to expect on pages without a text layer, 1 to 10 BCP 47 tags of 1 to 35 characters each, among `Limits.recognition_languages`, one part per value; another is refused `not_allowed`. Default detected: the document's declared language, else the language of its text, else the script found on the page. With no such page it has no effect and makes no notice.
    
</dd>
</dl>

<dl>
<dd>

**wait_seconds:** `typing.Optional[float]` — The most seconds this call may work before it answers, counted from the moment the work starts; time spent waiting to start is not counted. A parse that finishes inside it answers `201` with the record; one that needs more answers `202` with a job and runs on. 5 to 90; default 30.
    
</dd>
</dl>

<dl>
<dd>

**max_cost:** `typing.Optional[Money]` — The most this call may cost, a `Money` as a JSON part in the account's currency, reserved at the start against the balance and the budgets. A long scan is the most expensive call there is, since each recognized page bills two page units, so set it with that in mind. Default the key's cap on one call. A value below the smallest call's price is refused `cost-exceeds-cap`, with `minimum_cap`.
    
</dd>
</dl>

<dl>
<dd>

**max_source_price:** `typing.Optional[Money]` — The most you would allow getclean to pay a site that asks a price for the document at `url`, a `Money` as a JSON part; with `document` it does nothing, the notice `field_not_applicable`. getclean pays no site, whatever the value: a site that asks a price ends `payment_required`, with the price in `cost.source_price`. Default none.
    
</dd>
</dl>

<dl>
<dd>

**retention:** `typing.Optional[Retention]` — How long the record is kept. `none` keeps nothing past the delivery: when the parse ran as a job, the record waits for the first `get_contents`, which is its delivery, and is erased after that answer. `hold` keeps the record 48 hours after its last call, at most 30 days, and is allowed only under a `hold` policy, since a request never loosens the key. Default the key's `policy.retention`.
    
</dd>
</dl>

<dl>
<dd>

**pinned_version:** `typing.Optional[str]` — The version of getclean to run under, at most 64 characters; it fixes how documents are read and how pages are recognized, and `execution.version` equals it. Default the current version, `Limits.current_version`. A version not served, never or no longer, is `version-withdrawn`, with the versions served.
    
</dd>
</dl>

<dl>
<dd>

**run_id:** `typing.Optional[str]` — The run the record belongs to, an existing run of the key; a key has one run, `run_default`. Default the key's default run. An unknown run is refused `not_allowed`.
    
</dd>
</dl>

<dl>
<dd>

**metadata:** `typing.Optional[typing.Dict[str, str]]` — Your own labels, a JSON part, returned on the record as sent and never passed to a site: at most 20 string pairs, keys of 1 to 64 characters, values of 1 to 512. Default none. An empty map is refused `bound`.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/getclean/client.py">list_jobs</a>(...) -> SyncPager[Job, JobPage]</code></summary>
<dl>
<dd>

#### Description

<dl>
<dd>

<dl>
<dd>

List the account's jobs, newest first, free. `state` and `kind` filter them, and every filter you send must match. A job started while you page may make an item repeat; when you merge pages, keep one entry per `id`.

**What it costs.** The key needs `jobs:read`. The call is free. The answer is `200` with `JobPage`.

**Paging.** `page_size` from 1, default 50, maximum 200, a larger value lowered with the notice `page_size_lowered`; `page_token` is opaque, bound to its query, alive 24 hours; `next_page_token` is absent on the last page, and a page that carries it holds at least one job. A changed filter between pages, `page_size` excepted, or an unknown, expired or another list's token, is `400 page-token-invalid`.

**Refused before any work.** A value outside its set or range, `page_size` above its maximum excepted, which is lowered: `400 invalid-request`, `not_allowed` or `bound`, each with where it is. A token of another list: `400 page-token-invalid`. An unknown query parameter: `400 invalid-request`, `unknown_field`.

**Notices this operation makes.** `page_size_lowered`, in `JobPage.notices`; a `Job` carries no notices and no version, so no retirement notice is made here.

**Problem types.**
- 400 `invalid-request`, The request is invalid; `page-token-invalid`, The page token is invalid.
- 401 `unauthorized`, The key is missing or rejected.
- 403 `insufficient-scope`, The key lacks a scope this call needs.
- 429 `rate-limit-exceeded`, The rate limit is exceeded; `concurrency-limit-exceeded`, Too many calls are in flight.
- 500 `internal-error`, The service failed.
- 503 `overloaded`, The service is overloaded.
</dd>
</dl>
</dd>
</dl>

#### Usage

<dl>
<dd>

<dl>
<dd>

```python
from getclean import GetClean
from getclean.environment import GetCleanEnvironment

client = GetClean(
    environment=GetCleanEnvironment.PRODUCTION,
)

client.list_jobs(
    state="completed",
    kind="upload_contents",
)

```
</dd>
</dl>
</dd>
</dl>

#### Parameters

<dl>
<dd>

<dl>
<dd>

**state:** `typing.Optional[str]` — Only jobs in this state; `queued`, `running`, `completed`, `failed` or `canceled`, the last three final; an open set. Default none.
    
</dd>
</dl>

<dl>
<dd>

**kind:** `typing.Optional[str]` — Only jobs of this kind, `upload_contents`, an open set. Default none.
    
</dd>
</dl>

<dl>
<dd>

**page_size:** `typing.Optional[int]` — At most this many jobs on the page, from 1; default 50; the maximum, 200, stands in `Limits.bounds`, and a larger value is lowered with the notice `page_size_lowered`.
    
</dd>
</dl>

<dl>
<dd>

**page_token:** `typing.Optional[str]` — The next page, as the last answer's `next_page_token` gave it; opaque, at most 1,024 characters, never built by the caller. Default none, the first page.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/getclean/client.py">get_job</a>(...) -> Job</code></summary>
<dl>
<dd>

#### Description

<dl>
<dd>

<dl>
<dd>

Read a job, or wait for it to finish, free. The answer comes at the final state or when `wait_seconds` ends, with the job as it stands; it is `200` when the job failed too, with the failure inside. `Retry-After` and `retry_after_seconds` come on every answer that is not final. Once `contents_id` is set, `get_contents` reads the record; `cancel_job` asks the job to stop.

**What it costs.** The key needs `jobs:read`. The call is free. The answer is `200` with `Job`, never cached. A `HEAD` on this path is answered at once and does not wait.

**Refused before any work.** A value outside its range: `400 invalid-request`, `bound`. An id of the wrong kind: `400 invalid-request`, before any lookup. An unknown query parameter: `400 invalid-request`, `unknown_field`.

**Problem types.**
- 400 `invalid-request`, The request is invalid.
- 401 `unauthorized`, The key is missing or rejected.
- 403 `insufficient-scope`, The key lacks a scope this call needs.
- 404 `not-found`, Not found: an unknown or another account's job.
- 410 `job-expired`, The job has expired: the job ended more than 30 days ago. The answer comes for 30 more days, to the owning account only, with `expired_at` and `change` naming `upload_contents`; then `404`.
- 429 `rate-limit-exceeded`, The rate limit is exceeded; `concurrency-limit-exceeded`, Too many calls are in flight.
- 500 `internal-error`, The service failed.
- 503 `overloaded`, The service is overloaded.
</dd>
</dl>
</dd>
</dl>

#### Usage

<dl>
<dd>

<dl>
<dd>

```python
from getclean import GetClean
from getclean.environment import GetCleanEnvironment

client = GetClean(
    environment=GetCleanEnvironment.PRODUCTION,
)

client.get_job(
    job_id="job_8Rt2mqXKclxu58MCwLkSCV",
)

```
</dd>
</dl>
</dd>
</dl>

#### Parameters

<dl>
<dd>

<dl>
<dd>

**job_id:** `str` — The job, a `job_` id as `upload_contents` returned it.
    
</dd>
</dl>

<dl>
<dd>

**wait_seconds:** `typing.Optional[float]` — The most seconds to wait for the job to finish, 0 to 90; the answer comes at the final state or when the wait ends, with the current state. Default 0, no wait.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/getclean/client.py">cancel_job</a>(...) -> Job</code></summary>
<dl>
<dd>

#### Description

<dl>
<dd>

<dl>
<dd>

Ask a job to stop, free. The answer is `200` with the job as it stands; the work may finish before it stops, and `Retry-After` comes while it still runs, as on `get_job`. A job already final is unchanged. With pages already parsed the record is `partial`, `canceled`, the pages kept and billed; with none, no record and nothing billed.

**What it costs.** The key needs `jobs:cancel`. The call is free. It takes no body; a body sent is refused `400 invalid-request`.

**Refused before any work.** An id of the wrong kind: `400 invalid-request`, before any lookup. A body sent: `400 invalid-request`. An unknown query parameter: `400 invalid-request`, `unknown_field`.

**Problem types.**
- 400 `invalid-request`, The request is invalid.
- 401 `unauthorized`, The key is missing or rejected.
- 403 `insufficient-scope`, The key lacks a scope this call needs.
- 404 `not-found`, Not found: an unknown or another account's job.
- 410 `job-expired`, The job has expired: the job ended more than 30 days ago; the answer comes for 30 more days, to the owning account only, then `404`.
- 429 `rate-limit-exceeded`, The rate limit is exceeded; `concurrency-limit-exceeded`, Too many calls are in flight.
- 500 `internal-error`, The service failed.
- 503 `overloaded`, The service is overloaded.
</dd>
</dl>
</dd>
</dl>

#### Usage

<dl>
<dd>

<dl>
<dd>

```python
from getclean import GetClean
from getclean.environment import GetCleanEnvironment

client = GetClean(
    environment=GetCleanEnvironment.PRODUCTION,
)

client.cancel_job(
    job_id="job_3ZYgQAhOBQmM5xiilC8Fj9",
)

```
</dd>
</dl>
</dd>
</dl>

#### Parameters

<dl>
<dd>

<dl>
<dd>

**job_id:** `str` — The job to stop, a `job_` id.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/getclean/client.py">fetch_contents_batch</a>(...) -> ContentsBatch</code></summary>
<dl>
<dd>

#### Description

<dl>
<dd>

<dl>
<dd>

Fetch 1 to 20 pages or documents at their URLs in one call. You get one record per address, kept as a single fetch's is, with a tally first and the sum of the costs last.

Give it the addresses as `items`, each with its own few fields, and at the top the fields every item shares. The results come in input order, each a record or the problem that skipped it. Nothing here is atomic: an item that fails or is skipped leaves the others standing. The batch is not a resource, so it has no id, no expiry and no `Location`; each record has its own. Use `fetch_contents` for one address; use `upload_contents` for a file you hold. A batch takes at most 20 addresses and no files.

**What it costs.** The key needs `contents:fetch`, plus `contents:model` as on `fetch_contents`, decided over the top fields and every item before any work. The price is the sum of the records' costs, each priced as a fetch, with `units` summed by name. An item that was skipped, or whose record failed, was refused or needs a person, bills nothing.

**What comes back.** `200` with `ContentsBatch`: `counts`, how the items ended; `results`, in input order; `cost`, the sum. Every record is kept 48 hours after its last call and at most 30 days.

**The idempotency key.** `Idempotency-Key` is required here, since a repeated batch would fetch and bill every address twice; without it the call is `400 invalid-request` naming the header. The whole answer is stored when at least one record was billed, and the same key with the same body returns it again with this call's `request_id`, every record's `expires_at` as it stands and `replayed` true on every `cost`. The same key while the first call still runs is `409 idempotency-key-in-flight`; the same key with another body is `422 idempotency-key-reused`. A replay whose record was deleted is `404 not-found` naming the deletion.

**The bounds.**
- The body is at most 4 MiB, enough for 20 items with five 4,000-character highlights each in a script such as Chinese, where a character takes three bytes, JSON escaping included.
- `max_characters` bounds each record's text as on a fetch. `max_total_characters` bounds the whole answer's text, links counted by their url and text: records take their text in input order while it fits in what remains, and a record that would pass it comes as `sections_only` with the notice `total_characters_cut`; `get_contents` returns that record's text free unless `retention` is `none`. A value below `max_characters` is allowed.
- `screenshot` counts against neither bound and bills one `screenshots` unit per record that made one; `raw_html` counts against neither and is free.
- `wait_seconds` is each item's own deadline from its own start. Items run in parallel up to the key's concurrency and the rest wait inside the call; the whole call ends at `bounds.contents.batch_seconds`, and an item not started by then is `skipped` with the problem `overloaded` and `retry_after_seconds` set, never `deadline`.

**Money.** `max_cost` is the whole call's ceiling, reserved at the start in input order: each item its smallest call, one `contents`, a `baseline_fingerprint` item too, and the units it asks for by name, the model steps and the screenshot. An item's record carries the ceiling reserved for it as `cost.ceiling`. An item the remainder cannot cover for its smallest call is `skipped` with the problem of the limit that bound it: `cost-exceeds-cap` for this request's `max_cost`, `policy-limit-exceeded` for the key's cap, `credit-exhausted`, `run-budget-exhausted` or `key-budget-exhausted`. What remains of the ceiling is shared by the documents' pages, which spend it as they come; a document stops when it is spent, `partial`, `cost_capped`. Inside an item the extras are cut in the order `fetch_contents` gives, each with the notice `cost_cut`. `json_schema` and `summary` run per record, one model step per record per field.

**Faults, and whose they are.**
- The batch's own shape broken, a missing `url`, a bad or repeated `label`, a malformed `baseline_fingerprint`, a bound passed, a misplaced or unknown field: `422` for the whole call, each violation with its pointer, as `/items/3/url`.
- A top field's rule broken: `422` for the whole call, as on `fetch_contents`.
- One item's fault in its address, its domain or a legal demand: that item alone is `skipped`, its problem beside it, `invalid-field`, `destination-refused`, `policy-limit-exceeded` or `legal-block`, and the batch runs.
- One item's fault learned from the fetch: that item's record carries the outcome.
- The same URL twice: two fetches, two records.

**Refused before any work**, every violation of the body reported at once in `violations`:
- Fewer than 1 or more than 20 items: `invalid-field`, `bound`.
- An item without `url`: `required`.
- A `label` repeated: `duplicate`; one outside its character set or length: `syntax`, `bound`.
- `url`, `label`, `highlights` or `baseline_fingerprint` at the top, or a top-only field inside an item: `misplaced`.
- `max_total_characters` outside its range: `bound`.
- Every rule of `fetch_contents` on the top fields and on an item's own fields, except the address's own rules, its scheme and userinfo, the destination and the domain policy, which skip that item alone as said above.
- An unknown field, at the top or in an item: `unknown_field`.
- `Idempotency-Key` absent: `400 invalid-request`.

**Notices this operation makes.** Every notice of `fetch_contents`, inside each record; `total_characters_cut` on a record cut by the whole answer's bound.

**Problem types.** For the whole call:
- 400 `invalid-request`, The request is invalid.
- 401 `unauthorized`, The key is missing or rejected.
- 403 `insufficient-scope`, The key lacks a scope this call needs; `policy-limit-exceeded`, The key's policy forbids this; `credit-exhausted`, The credit is exhausted; `run-budget-exhausted`, The run's budget is exhausted; `key-budget-exhausted`, The key's budget is exhausted.
- 404 `not-found`, Not found, on a replay whose record was deleted.
- 409 `idempotency-key-in-flight`, The same request is still running.
- 413 `body-too-large`, The body is too large.
- 415 `unsupported-media-type`, The media type is not supported.
- 422 `invalid-field`, A field is invalid; `model-work-refused`, Model work is refused by the request; `cost-exceeds-cap`, The cost cap is below the smallest call; `version-withdrawn`, The version is no longer served; `idempotency-key-reused`, The idempotency key was reused with another body.
- 429 `rate-limit-exceeded`, The rate limit is exceeded; `concurrency-limit-exceeded`, Too many calls are in flight.
- 500 `internal-error`, The service failed.
- 503 `overloaded`, The service is overloaded.

Inside a skipped item, each without `status`: `invalid-field`, `destination-refused`, `policy-limit-exceeded`, `legal-block`, `cost-exceeds-cap`, `credit-exhausted`, `run-budget-exhausted`, `key-budget-exhausted`, `overloaded`.

**When a record is not delivered.** `outcome.message` says what may work next, and the table under `Outcome.reason` gives it for every reason.
</dd>
</dl>
</dd>
</dl>

#### Usage

<dl>
<dd>

<dl>
<dd>

```python
from getclean import GetClean, ContentsBatchItem, Money
from getclean.environment import GetCleanEnvironment

client = GetClean(
    environment=GetCleanEnvironment.PRODUCTION,
)

client.fetch_contents_batch(
    items=[
        ContentsBatchItem(
            url="https://a.example/report",
            label="a",
        ),
        ContentsBatchItem(
            url="https://b.example/filing",
            label="b",
            baseline_fingerprint="sha-256=:kw4QGoYGxOYpZ0EZGL+nxMfFUXfrxcp+P0M4EOrEiH4=:",
        ),
        ContentsBatchItem(
            url="http://10.0.0.7/admin",
            label="c",
        )
    ],
    max_total_characters=60000,
    max_cost=Money(
        amount="0.1000",
        currency="USD",
    ),
    formats=[
        "json"
    ],
    block_kinds=[
        "table"
    ],
)

```
</dd>
</dl>
</dd>
</dl>

#### Parameters

<dl>
<dd>

<dl>
<dd>

**items:** `typing.Sequence[ContentsBatchItem]` — The fetches, 1 to 20 `ContentsBatchItem` objects, answered in this order. Required. The same URL may stand twice and makes two records.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `typing.Optional[str]` 

One key per logical call, so a retry is never billed twice.

Required on this operation, where a duplicate would cost the most; without it the call is `400 invalid-request` naming the header. The SDKs fill a fresh key when you give none and send the same key on every retry of that call. Give your own key when your program retries across processes, so the second run finds the first answer.

The form: 1 to 255 visible ASCII characters, used exactly as sent, so a value written as a quoted Structured Field String keeps its quotes as part of the key. That is a stated departure from the IETF draft `draft-ietf-httpapi-idempotency-key-header`, revision 08, which is not yet a standard; this parameter documents the form in full.

What a repeated key does:
- The same key with the same body returns the first answer again, with this call's `request_id`, the current `expires_at` and `replayed` true on every `cost`. Nothing is billed again. On the upload the body is compared by a digest over the document and the fields, and a retried start with the same key is the same job.
- The same key while the first call still runs: `409 idempotency-key-in-flight`, with `Retry-After`.
- The same key with another body: `422 idempotency-key-reused`.

Answers are stored for 24 hours, per account, for billed answers and running jobs only. A call that may bill is kept in the store from its start, so a second call with its key meets the `409` while it runs.
    
</dd>
</dl>

<dl>
<dd>

**max_characters:** `typing.Optional[int]` — The most text to return per record, in characters. `0` returns no text but the map of sections and the facts. Default 20,000; `0`, or 1,000 to 1,000,000; a value between 1 and 999 is refused `bound`.
    
</dd>
</dl>

<dl>
<dd>

**max_total_characters:** `typing.Optional[int]` — The most text in the whole answer, every record's text and links together, links counted by their url and text. Records take their text in input order while it fits in what remains; a record that would pass it comes as `sections_only` with the notice `total_characters_cut`, and `get_contents` returns its text free. Default 200,000; 1,000 to 2,000,000, a value below `max_characters` allowed.
    
</dd>
</dl>

<dl>
<dd>

**wait_seconds:** `typing.Optional[float]` — The most seconds each item may work, counted from its own start, as on `fetch_contents`; the whole call ends at `bounds.contents.batch_seconds`, and an item not started by then is skipped. 5 to 90; default 30.
    
</dd>
</dl>

<dl>
<dd>

**max_cost:** `typing.Optional[Money]` — The most the whole call may cost, in the account's currency. It is reserved per item in input order, each item's smallest call and the units it asks for by name, and what remains is one shared sum the documents' pages spend. Default the key's cap on one call. A value below one item's smallest call is refused `cost-exceeds-cap`, with `minimum_cap`.
    
</dd>
</dl>

<dl>
<dd>

**scope:** `typing.Optional[Scope]` — Which view to return for every item: `main`, the main content alone, or `whole_page`, everything on the page. Default `main`. A document has one view, so `whole_page` on a document makes the notice `field_not_applicable`.
    
</dd>
</dl>

<dl>
<dd>

**formats:** `typing.Optional[typing.Sequence[str]]` — The formats to return for every item, 0 to 7 of these: `markdown`, the content as one markdown string; `html`, as clean HTML; `doclang`, as DocLang, an XML that keeps each block with its place on the page; `json`, as `Block` objects; `links`, every link with its kind; `screenshot`, a picture of the whole page; `raw_html`, the page's bytes exactly as served. `[]` returns the facts only. Default `["markdown"]`. An open set; a repeated value is refused `duplicate`, a value outside the set `not_allowed`. `doclang`, `screenshot` and `raw_html` apply to a web page only; on a document each makes the notice `field_not_applicable`.
    
</dd>
</dl>

<dl>
<dd>

**block_kinds:** `typing.Optional[typing.Sequence[str]]` — Keep only blocks of these kinds, in every format and in every model step, for every item: 1 to 10 of `text`, `heading`, `code`, `math`, `divider`, `interactive`, `table`, `image`, `embed`, `media`, an open set. Default: every kind. An empty list is refused `bound`.
    
</dd>
</dl>

<dl>
<dd>

**json_schema:** `typing.Optional[typing.Dict[str, typing.Any]]` — Your own fields, filled from each record by a model, each value with the words it came from; one model step per record, needs `contents:model`. As on `fetch_contents`: a JSON Schema 2020-12 object whose root is `type: object` with `properties`, at most 50 KB, refused `syntax` when it is not valid JSON Schema and `not_allowed` when its root is not `type: object`, it has no `properties`, or its `pattern` needs backtracking; `model-work-refused` under `deterministic_only`, `policy-limit-exceeded` under a key whose policy forbids model work. Default none.
    
</dd>
</dl>

<dl>
<dd>

**summary:** `typing.Optional[bool]` — Have a model write a summary of each record, at most 1,500 characters, in the content's language, as on `fetch_contents`; one model step per record, needs `contents:model`. Default false. Under `deterministic_only` it is refused `model-work-refused`; under a key whose policy forbids model work, `policy-limit-exceeded`.
    
</dd>
</dl>

<dl>
<dd>

**deterministic_only:** `typing.Optional[bool]` — Turn off, for every item, every step whose output could differ between two runs of the same input, as on `fetch_contents`: no judged highlight, no schema fill, no summary, and the publisher's kind only from what getclean already knows. Text recognition on a scanned page still runs and is listed, since it repeats under one version. Default false. A key whose policy forbids model work makes it true, with the notice `default_set_by_policy`; sending false under such a key is `policy-limit-exceeded`.
    
</dd>
</dl>

<dl>
<dd>

**as_of_date:** `typing.Optional[datetime.date]` — Read every page as an archive kept it on that day, the latest capture at or before the end of the day, UTC; an item's own `as_of_date` overrides it. A date not after today in UTC. Default none, the live pages.
    
</dd>
</dl>

<dl>
<dd>

**subject_country:** `typing.Optional[str]` — The country every page is read from, ISO 3166-1 alpha-2, one of the countries getclean can read from, `Limits.exits`; an item's own `subject_country` overrides it. Default the key's `default_exit`. A country getclean cannot read from is refused `not_allowed`, with the countries it can read from in `allowed_values`.
    
</dd>
</dl>

<dl>
<dd>

**subject_language:** `typing.Optional[str]` — The language to ask every site for, as its `Accept-Language`, a BCP 47 tag of 1 to 35 characters; an item's own `subject_language` overrides it. Default none: getclean sends its usual `Accept-Language`, which `source.visitor.language` reports.
    
</dd>
</dl>

<dl>
<dd>

**recognition_languages:** `typing.Optional[typing.Sequence[str]]` — The languages to expect on scanned pages, for every item that serves a document: 1 to 10 BCP 47 tags of 1 to 35 characters each, among `Limits.recognition_languages`; another is refused `not_allowed`. Default detected, as on `fetch_contents`.
    
</dd>
</dl>

<dl>
<dd>

**max_source_price:** `typing.Optional[Money]` — The most you would allow getclean to pay a site that asks a price for its page, for every item, as on `fetch_contents`. getclean pays no site, whatever the value: a page that asks a price ends that record `payment_required`, with the price in its `cost.source_price`. Default none.
    
</dd>
</dl>

<dl>
<dd>

**retention:** `typing.Optional[Retention]` — How long every record of the batch is kept, `hold` or `none`, as on `fetch_contents`. Default the key's `policy.retention`; `hold` is allowed only under a `hold` policy.
    
</dd>
</dl>

<dl>
<dd>

**pinned_version:** `typing.Optional[str]` — The version of getclean every item runs under, at most 64 characters; `execution.version` equals it on every record. Default the current version, `Limits.current_version`. A version not served, never or no longer, is `version-withdrawn`, with the versions served.
    
</dd>
</dl>

<dl>
<dd>

**run_id:** `typing.Optional[str]` — The run every record belongs to, an existing run of the key. Default the key's default run. An unknown run is refused `not_allowed`.
    
</dd>
</dl>

<dl>
<dd>

**metadata:** `typing.Optional[typing.Dict[str, str]]` — Your own labels, returned on every record as sent and never passed to a site: at most 20 string pairs, keys of 1 to 64 characters, values of 1 to 512. Default none. An empty map is refused `bound`.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/getclean/client.py">highlight_contents</a>(...) -> ContentsHighlights</code></summary>
<dl>
<dd>

#### Description

<dl>
<dd>

<dl>
<dd>

Find words or questions in a record you already have and mark where they stand, without fetching again. You get each place with its section and block ids, and, when you ask for text, the sections that hold them, marked. A string found verbatim is free; one a model has to judge costs one model step, once per call however many strings needed it.

**What it costs.** The key needs `contents:read`, and `contents:model` unless `deterministic_only` is true, since a string may need a model. Free when every string was found verbatim; 1 `model_steps` when any string had to be judged, once per call. The answer is `200` with `ContentsHighlights`; the call moves the record's `expires_at` 48 hours ahead.

**The idempotency key.** `Idempotency-Key` is optional here. A billed answer is stored 24 hours and replayed under the same key and body with this call's `request_id` and `replayed` true on `cost`; a free answer is not stored; the same key in flight is `409 idempotency-key-in-flight`; the same key with another body `422 idempotency-key-reused`.

**Each string.** Found `exact` when its words stand in one block, after Unicode normalization and whitespace collapse, case kept; `near` when they stand there after case folding, with ellipses and the punctuation at the ends of words removed, pieces in order, the dotted and dotless i of Turkic scripts folded to one; `judged` when not found verbatim and a model picked the blocks that bear on it; not found, and nothing bears on it, or `deterministic_only`: the notice `highlight_not_found`, one per string. Every occurrence is a highlight, in document order, at most 50, past which the notice `highlights_cut` comes.

**What comes back.** `max_characters: 0`: the `highlights` list with ids and places, no text, `formats` echoed `[]`. Above `0`: the sections holding highlights, in document order while they fit; a section larger than what remains comes cut at a block edge with its highlighted blocks inside; `truncated` true when the text returned is not the whole content, false when the holding sections are the whole and fit or when nothing was found; the rest through `get_section` or `list_blocks` with `block_ids`. The marks are `<mark id="h1">…</mark>` in `markdown` and `html` and `highlight_ids` on `blocks`; the record's own text never changes.

**Verbatim only.** Under `deterministic_only`, a key whose policy forbids model work, or a ceiling below a model step, the strings are matched verbatim only; this operation is never refused for the key's policy or the ceiling, an explicit `deterministic_only: false` under such a key excepted, `policy-limit-exceeded` as on the fetch; under a ceiling below the step the miss carries the notice `cost_cut` or `budget_cut` naming `highlights`. A model step that fails or passes its bound, `bounds.contents.model_step_seconds`, answers `200` with the verbatim results and the notice `step_failed`, not billed. `scope: whole_page` on a document record, or `block_kinds` that match no block, is the notice `field_not_applicable`; with no block to search nothing is found, nothing is judged, nothing billed.

**Refused before any work.** `doclang`, `links`, `screenshot` or `raw_html` in `formats`, or a value outside its set: `invalid-field`, `not_allowed`. `highlights` missing: `required`; an empty list: `bound`; a duplicate: `duplicate`. `max_characters` between 1 and 999, or any other bound passed: `bound`. An unknown field: `unknown_field`. A record that failed, was refused or needs a person: `409 record-without-content`, `change` naming `fetch_contents`. Every violation of the body is reported at once in `violations`.

**Notices this operation makes.** The record's own notices first, then `highlight_not_found`, `highlights_cut`, `step_failed`, `cost_cut`, `budget_cut`, `default_set_by_policy`, `field_not_applicable`, `version_retiring`.

**Problem types.** Never a money problem: when the money does not cover the model step, the strings are matched verbatim instead.
- 400 `invalid-request`, The request is invalid.
- 401 `unauthorized`, The key is missing or rejected.
- 403 `insufficient-scope`, The key lacks a scope this call needs; `policy-limit-exceeded`, The key's policy forbids this.
- 404 `not-found`, Not found.
- 409 `record-without-content`, The record has no content; `idempotency-key-in-flight`, The same request is still running.
- 410 `contents-expired`, The record has expired.
- 413 `body-too-large`, The body is too large.
- 415 `unsupported-media-type`, The media type is not supported.
- 422 `invalid-field`, A field is invalid; `idempotency-key-reused`, The idempotency key was reused with another body.
- 429 `rate-limit-exceeded`, The rate limit is exceeded; `concurrency-limit-exceeded`, Too many calls are in flight.
- 500 `internal-error`, The service failed.
- 503 `overloaded`, The service is overloaded.
</dd>
</dl>
</dd>
</dl>

#### Usage

<dl>
<dd>

<dl>
<dd>

```python
from getclean import GetClean
from getclean.environment import GetCleanEnvironment

client = GetClean(
    environment=GetCleanEnvironment.PRODUCTION,
)

client.highlight_contents(
    contents_id="cnt_3Fk9abaUhNX7t2eKkgfd3e",
    highlights=[
        "Revenue rose 12%",
        "dividend policy"
    ],
    max_characters=0,
)

```
</dd>
</dl>
</dd>
</dl>

#### Parameters

<dl>
<dd>

<dl>
<dd>

**contents_id:** `str` — The record, a `cnt_` id.
    
</dd>
</dl>

<dl>
<dd>

**highlights:** `typing.Sequence[str]` — Words or questions to find and mark; each string is one query, numbered by `query_index` in the answer. 1 to 5 strings, each 1 to 4,000 characters; an empty list is refused `bound`, a duplicate `duplicate`. Required.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `typing.Optional[str]` 

One key per logical call, so a retry is never billed twice.

Optional on this operation; required on `upload_contents`, `fetch_contents_batch` and `search_batch`, where a duplicate would cost the most. The SDKs fill a fresh key when you give none and send the same key on every retry of that call. Give your own key when your program retries across processes, so the second run finds the first answer.

The form: 1 to 255 visible ASCII characters, used exactly as sent, so a value written as a quoted Structured Field String keeps its quotes as part of the key. That is a stated departure from the IETF draft `draft-ietf-httpapi-idempotency-key-header`, revision 08, which is not yet a standard; this parameter documents the form in full.

What a repeated key does:
- The same key with the same body returns the first answer again, with this call's `request_id`, `expires_at` as it stands and `replayed` true on every `cost`. Nothing is billed again.
- The same key while the first call still runs: `409 idempotency-key-in-flight`, with `Retry-After`.
- The same key with another body: `422 idempotency-key-reused`.

Answers are stored for 24 hours, per account, for billed answers and running jobs only; a free answer is not stored. A call that may bill is kept in the store from its start, so a second call with its key meets the `409` while it runs.
    
</dd>
</dl>

<dl>
<dd>

**max_characters:** `typing.Optional[int]` — The most text returned around the highlights, in characters; `0` means the list of places only. `0`, or 1,000 to 1,000,000; a value between 1 and 999 is refused `bound`. Default 20,000.
    
</dd>
</dl>

<dl>
<dd>

**scope:** `typing.Optional[Scope]` — Which view is searched, `main` or `whole_page`. Default the record's own.
    
</dd>
</dl>

<dl>
<dd>

**formats:** `typing.Optional[typing.Sequence[str]]` — The format of the text returned, when any: 1 to 3 of `markdown`, `html`, `json`; `doclang`, `links`, `screenshot` and `raw_html` are refused `not_allowed` here. Default `["markdown"]`.
    
</dd>
</dl>

<dl>
<dd>

**block_kinds:** `typing.Optional[typing.Sequence[str]]` — Search and return only these blocks, 1 to 10 of `text`, `heading`, `code`, `math`, `divider`, `interactive`, `table`, `image`, `embed`, `media`; an open set. Default: every kind. When none matches, the notice `field_not_applicable`.
    
</dd>
</dl>

<dl>
<dd>

**deterministic_only:** `typing.Optional[bool]` — Find the strings verbatim only: a string not found is the notice `highlight_not_found`, and no model judges it. Default false.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/getclean/client.py">fill_schema</a>(...) -> SchemaFill</code></summary>
<dl>
<dd>

#### Description

<dl>
<dd>

<dl>
<dd>

Fill your JSON Schema from a record you already have. You get a value only where the record states it, never a plausible one, with the place and the cited words for each property, and `empty`, `absent` or `unread` where the record says nothing. It is the same step as `fetch_contents`'s `json_schema`, run on the copy getclean keeps.

**What it costs.** The key needs `contents:model`. The price is 1 `model_steps`. The answer is `200` with `SchemaFill`; the call moves the record's `expires_at` 48 hours ahead.

**The idempotency key.** `Idempotency-Key` is optional here. The billed answer is stored 24 hours and replayed under the same key and body with this call's `request_id` and `replayed` true on `cost`; the same key in flight is `409 idempotency-key-in-flight`; the same key with another body `422 idempotency-key-reused`.

**The fill.** `schema_statuses` is keyed by JSON Pointer, one per property, with `text` the cited words and the place. `absent` means the content kept under `scope` says nothing; `unread` means the place may lie in parts not parsed, not recognized or past a cap, so absence cannot be claimed; an agent that meets `absent` beside a non-empty `left_out` may retry under `scope: whole_page`. `schema_values` carries no link and no image markup; a URL value is kept only when it stands in the record's links or text, otherwise removed with the notice `model_link_removed`. The step is the whole call: a step that gave a bad answer is `502 gateway-error`, a step that passed `bounds.contents.model_step_seconds` is `504 gateway-timeout`, each `retryable` true and not billed. `scope: whole_page` on a document record, or `block_kinds` that match no block, is the notice `field_not_applicable`; with no block to read every status is `absent` and the step is not billed.

**Refused before any work.** `json_schema` missing: `invalid-field`, `required`. A schema that is not valid JSON Schema 2020-12: `syntax`; one whose root is not `type: object`, that has no `properties`, or whose `pattern` needs backtracking: `not_allowed`. A value outside its set: `not_allowed`; a bound passed: `bound`; an unknown field: `unknown_field`. A key whose policy forbids model work, or whose cap is below a model step: `403 policy-limit-exceeded`. A record that failed, was refused or needs a person: `409 record-without-content`. Every violation of the body is reported at once in `violations`.

**Notices this operation makes.** The record's own notices first, then `model_link_removed`, `field_not_applicable`, `version_retiring`.

**Problem types.**
- 400 `invalid-request`, The request is invalid.
- 401 `unauthorized`, The key is missing or rejected.
- 403 `insufficient-scope`, The key lacks a scope this call needs; `policy-limit-exceeded`, The key's policy forbids this; `credit-exhausted`, The credit is exhausted; `run-budget-exhausted`, The run's budget is exhausted; `key-budget-exhausted`, The key's budget is exhausted.
- 404 `not-found`, Not found.
- 409 `record-without-content`, The record has no content; `idempotency-key-in-flight`, The same request is still running.
- 410 `contents-expired`, The record has expired.
- 413 `body-too-large`, The body is too large.
- 415 `unsupported-media-type`, The media type is not supported.
- 422 `invalid-field`, A field is invalid; `idempotency-key-reused`, The idempotency key was reused with another body.
- 429 `rate-limit-exceeded`, The rate limit is exceeded; `concurrency-limit-exceeded`, Too many calls are in flight.
- 500 `internal-error`, The service failed.
- 502 `gateway-error`, A step behind the service failed: the model step gave a bad answer; nothing was billed, and a retry may work.
- 503 `overloaded`, The service is overloaded.
- 504 `gateway-timeout`, A step behind the service timed out: the model step passed its time bound; nothing was billed, and a retry may work.
</dd>
</dl>
</dd>
</dl>

#### Usage

<dl>
<dd>

<dl>
<dd>

```python
from getclean import GetClean
from getclean.environment import GetCleanEnvironment

client = GetClean(
    environment=GetCleanEnvironment.PRODUCTION,
)

client.fill_schema(
    contents_id="cnt_3Fk9abaUhNX7t2eKkgfd3e",
    json_schema={
        "type": "object",
        "properties": {"revenue_growth": {"type": "string"}, "dividend": {"type": "string"}}
    },
)

```
</dd>
</dl>
</dd>
</dl>

#### Parameters

<dl>
<dd>

<dl>
<dd>

**contents_id:** `str` — The record, a `cnt_` id.
    
</dd>
</dl>

<dl>
<dd>

**json_schema:** `typing.Dict[str, typing.Any]` — The properties to fill, a JSON Schema 2020-12 object whose root is `type: object` with `properties`, at most 50 KB; refused `syntax` when it is not valid JSON Schema, `not_allowed` when its root is not `type: object`, it has no `properties`, or its `pattern` needs backtracking. Required.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `typing.Optional[str]` 

One key per logical call, so a retry is never billed twice.

Optional on this operation; required on `upload_contents`, `fetch_contents_batch` and `search_batch`, where a duplicate would cost the most. The SDKs fill a fresh key when you give none and send the same key on every retry of that call. Give your own key when your program retries across processes, so the second run finds the first answer.

The form: 1 to 255 visible ASCII characters, used exactly as sent, so a value written as a quoted Structured Field String keeps its quotes as part of the key. That is a stated departure from the IETF draft `draft-ietf-httpapi-idempotency-key-header`, revision 08, which is not yet a standard; this parameter documents the form in full.

What a repeated key does:
- The same key with the same body returns the first answer again, with this call's `request_id`, `expires_at` as it stands and `replayed` true on every `cost`. Nothing is billed again.
- The same key while the first call still runs: `409 idempotency-key-in-flight`, with `Retry-After`.
- The same key with another body: `422 idempotency-key-reused`.

Answers are stored for 24 hours, per account, for billed answers and running jobs only; a free answer is not stored. A call that may bill is kept in the store from its start, so a second call with its key meets the `409` while it runs.
    
</dd>
</dl>

<dl>
<dd>

**block_kinds:** `typing.Optional[typing.Sequence[str]]` — Read only these blocks, 1 to 10 of `text`, `heading`, `code`, `math`, `divider`, `interactive`, `table`, `image`, `embed`, `media`; an open set. Default: every kind. When none matches, the notice `field_not_applicable` and every status `absent`.
    
</dd>
</dl>

<dl>
<dd>

**scope:** `typing.Optional[Scope]` — Which view is read, `main` or `whole_page`. Default the record's own.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/getclean/client.py">summarize_contents</a>(...) -> ContentsSummary</code></summary>
<dl>
<dd>

#### Description

<dl>
<dd>

<dl>
<dd>

Have a model write a summary of a record you already have, at most 1,500 characters in the content's language, from the copy getclean keeps. It is the same step as `fetch_contents`'s `summary`. Use `highlight_contents` to find words and `fill_schema` to fill fields.

**What it costs.** The key needs `contents:model`. The price is 1 `model_steps`. The answer is `200` with `ContentsSummary`; the call moves the record's `expires_at` 48 hours ahead.

**The idempotency key.** `Idempotency-Key` is optional here. The billed answer is stored 24 hours and replayed under the same key and body with this call's `request_id` and `replayed` true on `cost`; the same key in flight is `409 idempotency-key-in-flight`; the same key with another body `422 idempotency-key-reused`.

**The summary.** At most 1,500 characters, in the content's language; no link and no image markup, any the model writes removed with the notice `model_link_removed`. The step is the whole call: a step that gave a bad answer is `502 gateway-error`, a step that passed `bounds.contents.model_step_seconds` is `504 gateway-timeout`, each `retryable` true and not billed. `scope: whole_page` on a document record, or `block_kinds` that match no block, is the notice `field_not_applicable`; with no block to read the summary is an empty string and the step is not billed.

**Refused before any work.** A value outside its set: `invalid-field`, `not_allowed`; a bound passed: `bound`; an unknown field: `unknown_field`. A key whose policy forbids model work, or whose cap is below a model step: `403 policy-limit-exceeded`. A record that failed, was refused or needs a person: `409 record-without-content`. Every violation of the body is reported at once in `violations`.

**Notices this operation makes.** The record's own notices first, then `model_link_removed`, `field_not_applicable`, `version_retiring`.

**Problem types.** The same as `fill_schema`.
- 400 `invalid-request`, The request is invalid.
- 401 `unauthorized`, The key is missing or rejected.
- 403 `insufficient-scope`, The key lacks a scope this call needs; `policy-limit-exceeded`, The key's policy forbids this; `credit-exhausted`, The credit is exhausted; `run-budget-exhausted`, The run's budget is exhausted; `key-budget-exhausted`, The key's budget is exhausted.
- 404 `not-found`, Not found.
- 409 `record-without-content`, The record has no content; `idempotency-key-in-flight`, The same request is still running.
- 410 `contents-expired`, The record has expired.
- 413 `body-too-large`, The body is too large.
- 415 `unsupported-media-type`, The media type is not supported.
- 422 `invalid-field`, A field is invalid; `idempotency-key-reused`, The idempotency key was reused with another body.
- 429 `rate-limit-exceeded`, The rate limit is exceeded; `concurrency-limit-exceeded`, Too many calls are in flight.
- 500 `internal-error`, The service failed.
- 502 `gateway-error`, A step behind the service failed: the model step gave a bad answer; nothing was billed, and a retry may work.
- 503 `overloaded`, The service is overloaded.
- 504 `gateway-timeout`, A step behind the service timed out: the model step passed its time bound; nothing was billed, and a retry may work.
</dd>
</dl>
</dd>
</dl>

#### Usage

<dl>
<dd>

<dl>
<dd>

```python
from getclean import GetClean
from getclean.environment import GetCleanEnvironment

client = GetClean(
    environment=GetCleanEnvironment.PRODUCTION,
)

client.summarize_contents(
    contents_id="cnt_3Fk9abaUhNX7t2eKkgfd3e",
)

```
</dd>
</dl>
</dd>
</dl>

#### Parameters

<dl>
<dd>

<dl>
<dd>

**contents_id:** `str` — The record, a `cnt_` id.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `typing.Optional[str]` 

One key per logical call, so a retry is never billed twice.

Optional on this operation; required on `upload_contents`, `fetch_contents_batch` and `search_batch`, where a duplicate would cost the most. The SDKs fill a fresh key when you give none and send the same key on every retry of that call. Give your own key when your program retries across processes, so the second run finds the first answer.

The form: 1 to 255 visible ASCII characters, used exactly as sent, so a value written as a quoted Structured Field String keeps its quotes as part of the key. That is a stated departure from the IETF draft `draft-ietf-httpapi-idempotency-key-header`, revision 08, which is not yet a standard; this parameter documents the form in full.

What a repeated key does:
- The same key with the same body returns the first answer again, with this call's `request_id`, `expires_at` as it stands and `replayed` true on every `cost`. Nothing is billed again.
- The same key while the first call still runs: `409 idempotency-key-in-flight`, with `Retry-After`.
- The same key with another body: `422 idempotency-key-reused`.

Answers are stored for 24 hours, per account, for billed answers and running jobs only; a free answer is not stored. A call that may bill is kept in the store from its start, so a second call with its key meets the `409` while it runs.
    
</dd>
</dl>

<dl>
<dd>

**block_kinds:** `typing.Optional[typing.Sequence[str]]` — Summarize only these blocks, 1 to 10 of `text`, `heading`, `code`, `math`, `divider`, `interactive`, `table`, `image`, `embed`, `media`; an open set. Default: every kind. When none matches, the notice `field_not_applicable` and an empty summary.
    
</dd>
</dl>

<dl>
<dd>

**scope:** `typing.Optional[Scope]` — Which view is summarized, `main` or `whole_page`. Default the record's own.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/getclean/client.py">compare_contents</a>(...) -> SyncPager[BlockChange, Comparison]</code></summary>
<dl>
<dd>

#### Description

<dl>
<dd>

<dl>
<dd>

Compare a record you already have with a baseline, block by block and cell by cell, without a model, free. You get whether anything changed, a tally, and each change with both of its sides. The baseline is another record, `baseline_contents_id`, or the markdown you kept yourself as a record returned it, `baseline_markdown` with its `baseline_fingerprint`. It is a `POST` with a body that bills nothing and changes nothing but the record's `expires_at`, so it is safe to repeat.

**What it costs.** The key needs `contents:read`. The call is free. The answer is `200` with `Comparison`; the call moves the current record's `expires_at` 48 hours ahead. The body is at most 8 MiB, so that a baseline of 1,000,000 characters fits in any script.

**The comparison.**
- A baseline you kept yourself is checked first: the sha-256 of the text, after the same normalization as the fingerprint, must equal `baseline_fingerprint`, else `422 invalid-field`, `syntax`, naming `baseline_fingerprint`. The text is split into blocks by the rules that made it, `baseline.verified` is true, and the `before` sides carry text without ids.
- Both sides must share one `execution.version` and one `record_scope`, else `422 records-incomparable` with `change` naming which. A difference in the kind of source or the configuration is the notice `fingerprint_incomparable`, and the comparison runs. A baseline you kept names its version and scope in `baseline_version` and `baseline_scope`, or takes the current record's.
- The unit is the block. Text is compared after Unicode normalization with the formatting marks removed; tables cell by cell; no model.
- `changed` blocks are paired in order when they are alike above a published similarity; `moved` is the same text at another position in the block order; `added` and `removed` are the rest, removed blocks at the place they held. A page number differing alone is no change, and a paragraph that runs across a page break is one block.
- `changed` true with `changes` `[]` means only inline formatting moved. The same id on both sides is `changed` false with `changes` `[]`.
- Two records of different URLs or documents are allowed; you know what you compare. `paywall_declared` is repeated when either side carries it.

**Paging.** `changes` is paged, `counts` the whole tally on every page before the rows; `page_size` from 1, default 50, maximum 200, a larger value lowered with the notice `page_size_lowered`; `page_token` binds the body's other fields, `page_size` included; a token of another comparison, or of this one with another body, is `400 page-token-invalid`.

**Refused before any work.** `baseline_contents_id` and `baseline_markdown` both present: `invalid-field`, `exclusive`; neither: `required`; `baseline_markdown` without `baseline_fingerprint` or the reverse: `dependent`; `baseline_version` or `baseline_scope` with `baseline_contents_id`: `dependent`. The text does not hash to `baseline_fingerprint`: `invalid-field`, `syntax`. A bound passed, `page_size` above its maximum excepted, which is lowered: `bound`; an unknown field: `unknown_field`. Another version or scope: `422 records-incomparable`, `change.field` naming `baseline_version` or `baseline_scope`, `baseline_contents_id` for a baseline that is a record. Either record without content: `409 record-without-content`, `change.field` naming the side. A token of another comparison, or of this one with another body: `400 page-token-invalid`. An id of the wrong kind: `400 invalid-request`. Every violation of the body is reported at once in `violations`.

**Notices this operation makes.** `fingerprint_incomparable`, `paywall_declared`, `page_size_lowered`, `version_retiring`.

**Problem types.**
- 400 `invalid-request`, The request is invalid; `page-token-invalid`, The page token is invalid.
- 401 `unauthorized`, The key is missing or rejected.
- 403 `insufficient-scope`, The key lacks a scope this call needs.
- 404 `not-found`, Not found, `change.field` saying which id.
- 409 `record-without-content`, The record has no content.
- 410 `contents-expired`, The record has expired, `detail` naming which record.
- 413 `body-too-large`, The body is too large.
- 415 `unsupported-media-type`, The media type is not supported.
- 422 `invalid-field`, A field is invalid; `records-incomparable`, The records cannot be compared.
- 429 `rate-limit-exceeded`, The rate limit is exceeded; `concurrency-limit-exceeded`, Too many calls are in flight.
- 500 `internal-error`, The service failed.
- 503 `overloaded`, The service is overloaded.
</dd>
</dl>
</dd>
</dl>

#### Usage

<dl>
<dd>

<dl>
<dd>

```python
from getclean import GetClean
from getclean.environment import GetCleanEnvironment

client = GetClean(
    environment=GetCleanEnvironment.PRODUCTION,
)

client.compare_contents(
    contents_id="cnt_9Zze6X8RDFg2XxyKyLlV5T",
    baseline_contents_id="cnt_3Fk9abaUhNX7t2eKkgfd3e",
)

```
</dd>
</dl>
</dd>
</dl>

#### Parameters

<dl>
<dd>

<dl>
<dd>

**contents_id:** `str` — The current record, a `cnt_` id.
    
</dd>
</dl>

<dl>
<dd>

**baseline_contents_id:** `typing.Optional[str]` — The baseline record, a `cnt_` id kept by the same account. One of `baseline_contents_id` and `baseline_markdown` is required; both at once are refused `exclusive`.
    
</dd>
</dl>

<dl>
<dd>

**baseline_markdown:** `typing.Optional[str]` — The markdown you kept, as a record returned it, whole, at most 1,000,000 characters; a partial text cannot be compared, since its hash is checked. With `baseline_fingerprint`, each refused `dependent` without the other.
    
</dd>
</dl>

<dl>
<dd>

**baseline_fingerprint:** `typing.Optional[str]` — The fingerprint of `baseline_markdown` as the record returned it; a text that does not hash to it is refused `syntax`.
    
</dd>
</dl>

<dl>
<dd>

**baseline_version:** `typing.Optional[str]` — The `execution.version` of the record your text came from, at most 64 characters, so the one-version rule can be checked and the text split by the rules that made it; with `baseline_markdown` only, refused `dependent` with `baseline_contents_id`. Default the current record's.
    
</dd>
</dl>

<dl>
<dd>

**baseline_scope:** `typing.Optional[Scope]` — The `record_scope` of the record your text came from; with `baseline_markdown` only, refused `dependent` with `baseline_contents_id`. Default the current record's.
    
</dd>
</dl>

<dl>
<dd>

**page_size:** `typing.Optional[int]` — At most this many changes on the page, from 1; default 50; the maximum, 200, stands in `Limits.bounds`, and a larger value is lowered with the notice `page_size_lowered`.
    
</dd>
</dl>

<dl>
<dd>

**page_token:** `typing.Optional[str]` — The next page of changes, as the last answer's `next_page_token` gave it; bound to this comparison and the body's other fields, `page_size` included. Default none, the first page.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/getclean/client.py">get_limits</a>() -> Limits</code></summary>
<dl>
<dd>

#### Description

<dl>
<dd>

<dl>
<dd>

Read your key's limits and your account's money in one answer, free, before a batch or any call that must fit a budget. You get the prepaid balance after the sums reserved by calls in flight, the use of the current period, every unit's price, the key's cap on one call and its budgets, its rate and the calls allowed in flight at once, the published bounds of both families, the document types taken, the countries getclean can read from, the recognition languages, the archives, the key's policy, and the versions served with the current one. There is no estimate operation: `max_cost` is the protection, and `prices` gives every unit's price.

**What it costs.** The key needs `limits:read`. The call is free. The answer is `200` with `Limits`, never cached, since it is the key's own.

**Refused before any work.** An unknown query parameter: `400 invalid-request`, `unknown_field`.

**Problem types.**
- 400 `invalid-request`, The request is invalid.
- 401 `unauthorized`, The key is missing or rejected.
- 403 `insufficient-scope`, The key lacks a scope this call needs.
- 429 `rate-limit-exceeded`, The rate limit is exceeded; `concurrency-limit-exceeded`, Too many calls are in flight.
- 500 `internal-error`, The service failed.
- 503 `overloaded`, The service is overloaded.
</dd>
</dl>
</dd>
</dl>

#### Usage

<dl>
<dd>

<dl>
<dd>

```python
from getclean import GetClean
from getclean.environment import GetCleanEnvironment

client = GetClean(
    environment=GetCleanEnvironment.PRODUCTION,
)

client.get_limits()

```
</dd>
</dl>
</dd>
</dl>

#### Parameters

<dl>
<dd>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/getclean/client.py">search</a>(...) -> Search</code></summary>
<dl>
<dd>

#### Description

<dl>
<dd>

<dl>
<dd>

Search up to ten datasources with one question, in up to twenty wordings, and get one ranked list of results with the facts of each and a receipt of what ran where, before any page is read. Each result is a lead, the one page shown for a group of copies. The search is kept as a record, so its full list is read again free, and every cut, skip or change is named in the answer. Use `contents` to fetch the top leads in the same call, `fetch_contents` to read one by its URL, and `list_datasources` to see what can be searched.

**What it costs.** The key needs `search:run`, which covers everything a search does, the inline fetches and their model fields included, under the key's policy. The price is 1 `searches`, plus 1 `datasource_queries` per source per wording that ran, plus 1 `model_steps` for the ranking and 1 for the choice of sources when they ran, plus the inline fetches priced as `fetch_contents`; a ranking cut by the deadline is not billed. The answer is `201 Created` with `Location` naming the record, `Search`. The record is kept 48 hours after its last call and at most 30 days from its making; `get_search` pages the list the search stored and never searches again or charges. A search answers within `wait_seconds`; what did not finish is named in a `partial` outcome. There is no job, no stream and no webhook.

**The idempotency key.** `Idempotency-Key` is optional here. The same key with the same body returns the first answer again with this call's `request_id`, the current `expires_at` and `replayed` true on every `cost`, no second charge; the same key in flight is `409 idempotency-key-in-flight`; the same key with another body `422 idempotency-key-reused`.

**The default call**, `{"query": "…"}`: the web plus the groups a model picks; ten results from each source per wording; ranked by a model; ten leads with 600-character excerpts and their publisher profiles; moderate safe search; ten seconds; the full record; the key's default run. Two model steps run by default, the ranking and the choice of sources when none are named, and a third identifies the publisher of a site getclean has not seen before; `deterministic_only` turns all three off.

**Languages.** A wording runs only on a source that covers its language. The web source takes every wording, each in its own language, searched from `subject_country`; a source in one language takes only wordings in that language; a source with one index per language takes each wording in its own index. A wording no source covers is a coverage gap, with the hint to add a wording in the source's language. `languages` restricts the pages returned and is independent of this. Nothing is translated. With `subject_identifiers` and no `query`, each identifier's value runs as a wording with origin `identifier`.

**The inline fetch.** `contents.top` of the leads are fetched in the same call, each as a contents record under `fetch_contents`'s rules.
- It takes the search's `as_of_date`, `pinned_version`, `run_id`, `deterministic_only`, `retention` and `max_source_price`, and its `subject_country` when that is a country getclean can read from, else the key's `default_exit` with the notice `field_not_applicable`.
- A lead found through a registered datasource is fetched under that datasource's login, the one way to use a login on a fetch.
- Its time comes out of the search's `wait_seconds`, and it runs under what remains of the search's ceiling at its turn. Each inline record carries its own `cost`.
- At the deadline the record follows the contents' rules. A fetch not started by the deadline makes no record, and the search ends `partial`, `fetches_missing`, with the notice `fetch_not_finished`.
- `contents.max_characters` bounds one page. `max_total_characters` bounds the whole answer's text, excerpts and fetched pages together: the excerpts first, cut from the last lead backwards when they alone pass it, then the fetched pages in rank order while they fit in what remains; a page that would pass it comes as `sections_only`; each cut makes the notice `total_characters_cut`.

**Money.** The ceiling is the lowest of the request's `max_cost`, the key's cap, the run's budget, the key's budget and the balance. When it cannot cover everything, the extras are cut in this order, each with the notice `cost_cut`: first each inline fetch's own extras, in the order `fetch_contents` gives; then whole fetches, the search ending `partial`, `fetches_missing`; then the ranking, `partial`, `rerank_missing`; then the choice of sources; then the results taken per source. `max_source_price` is the most you allow for a datasource that charges per query, or for a site an inline fetch meets that asks a price; a source whose fee passes it is not searched, the coverage gap `over_price`. getclean pays no site for a page, so a page that asks a price ends `payment_required`.

**Said, never refused.** A hard filter a source cannot apply and cannot emulate: that source skipped, in `coverage_gaps`, the filter named. A wording in a language no source covers: `coverage_gaps`. `source_independence`, or `independent` in `ranking_priorities`, with no subject resolved: notice `field_not_applicable`. A window later than `as_of_date`, or a per-site cap on one allowed site: a notice. `datasources` absent under `deterministic_only`: the receipt shows `web` only. The inline fetch's `subject_country` not in `Limits.exits`: notice `field_not_applicable`, the key's `default_exit` used. `max_source_price` below a datasource's fee: that source skipped, coverage gap `over_price`. An `issuer` sent with a scheme that takes none: notice `field_not_applicable`, the identifier runs by its `scheme` and `value`.

**Fields that read alike.** `allowed_domains` names sites that count, names with dots; `datasources` names places to search, names without. `allowed_domains` is hard, only these; `ranking_preferred_domains` is soft, these first and the rest still count. `subject_country` is where the search is made from; `languages` is what the pages are written in. `published_from` is the page's own date; `as_of_date` the source's state on a past day. `pinned_version` is getclean's version; `as_of_date` the sources' day. `purpose` is why, for the record and every model step; `ranking_instructions` is how to rank. `ranking_priorities` says which source facts go first; `ranking_order` how the rest is ordered. `source_kinds` is a filter that removes; `ranking_priorities: official` a preference that reorders. `max_per_datasource` is taken from each source before merging; `ranking_max_per_domain` is kept from each site in the answer. `max_candidates` is how many leads; `contents.top` how many of them to fetch. `max_excerpt_characters` is per lead, `max_total_characters` the whole answer, `contents.max_characters` one page fetched. Leaving the model fields out still runs the ranking and the choice of sources; `deterministic_only` turns every judging step off. `view` is how much of the record comes back; `record_form` the form the record is written in.

**Refused before any work**, every violation of the body reported at once in `violations`:
- Neither `query` nor `subject_identifiers`: `invalid-field`, `required`.
- `alternate_queries` without `query`: `dependent`.
- A scheme that needs an issuer, without one: `dependent`; an `issuer` no catalog entry lists for its scheme: `not_allowed`, with the listed codes in `allowed_values`.
- `published_within_days` with `published_from` or `published_until`: `exclusive`; `published_until` before `published_from`: `order`; a date after today: `bound`.
- A site in both `allowed_domains` and `blocked_domains`: `exclusive`; a `ranking_preferred_domains` value outside `allowed_domains` when that is set, or in `blocked_domains`: `dependent`.
- A site name in `datasources`, or a datasource id in `allowed_domains`, `blocked_domains` or `ranking_preferred_domains`: `misplaced`, `change.field` naming the field it belongs in.
- `contents` without `top`: `required`; `top` above 10: `bound`; `top` above `max_candidates`: `order`; `contents` with `wait_seconds` below 5, the least a fetch needs: `order`.
- Under `deterministic_only`: `ranking_instructions`, and `json_schema` or `summary` inside `contents`: `model-work-refused`.
- More than 20 wordings after OR splits: `bound`, with the count.
- `max_cost` below the smallest call's price, one `searches` and one `datasource_queries`: `cost-exceeds-cap`, with `minimum_cap`.
- `max_total_characters` below `max_excerpt_characters`: `order`.
- A source getclean cannot search: `datasource-not-searchable`. Every named source behind a login the key has not registered: `403 datasource-access-required`; one such source among others is the coverage gap `access_needed`, and the rest run.
- `safe_search` or `deterministic_only` looser than the key's policy, or `allowed_domains` widening the key's domain policy: `403 policy-limit-exceeded`.
- A value of `source_kinds`, `source_independence`, `ranking_priorities` or `ranking_order` outside its set: `not_allowed`.
- Every source would be skipped before work: `no-datasource-can-run`.
- An unknown datasource id: `datasource-unknown`; an unknown `set:NAME`: `domain-set-unknown`.
- A bare `pdf` in `media_types`: `not_allowed`, with `application/pdf` suggested.
- Any other bound passed: `bound`; an unknown field: `unknown_field`.
- `pinned_version` not served, never or no longer: `version-withdrawn`.

**Notices this operation makes.** `query_corrected`, `filter_emulated`, `default_set_by_policy`, `window_after_as_of_date`, `fetch_not_finished`, `cost_cut`, `budget_cut`, `time_cut`, `field_not_applicable`, `total_characters_cut` on the search and on an inline record, `version_retiring`. A skipped source is a coverage gap, never a notice too.

**Problem types.** A source's failure is never an API problem; it stands as that source's outcome in the receipt.
- 400 `invalid-request`, The request is invalid.
- 401 `unauthorized`, The key is missing or rejected.
- 403 `insufficient-scope`, The key lacks a scope this call needs; `policy-limit-exceeded`, The key's policy forbids this; `datasource-access-required`, The datasource needs a registered login; `credit-exhausted`, The credit is exhausted; `run-budget-exhausted`, The run's budget is exhausted; `key-budget-exhausted`, The key's budget is exhausted.
- 409 `idempotency-key-in-flight`, The same request is still running.
- 413 `body-too-large`, The body is too large.
- 415 `unsupported-media-type`, The media type is not supported.
- 422 `invalid-field`, A field is invalid; `model-work-refused`, Model work is refused by the request; `cost-exceeds-cap`, The cost cap is below the smallest call; `version-withdrawn`, The version is no longer served; `idempotency-key-reused`, The idempotency key was reused with another body; `no-datasource-can-run`, No datasource can run this search; `datasource-unknown`, The datasource is unknown; `datasource-not-searchable`, The datasource has no search; `domain-set-unknown`, The domain set is unknown.
- 429 `rate-limit-exceeded`, The rate limit is exceeded; `concurrency-limit-exceeded`, Too many calls are in flight.
- 451 `legal-block`, Withheld under a legal demand.
- 500 `internal-error`, The service failed.
- 503 `overloaded`, The service is overloaded.
</dd>
</dl>
</dd>
</dl>

#### Usage

<dl>
<dd>

<dl>
<dd>

```python
from getclean import GetClean, SearchContentsOptions, Money
from getclean.environment import GetCleanEnvironment

client = GetClean(
    environment=GetCleanEnvironment.PRODUCTION,
)

client.search(
    query="EU AI Act article 50 marking obligations",
    published_within_days=365,
    max_candidates=3,
    contents=SearchContentsOptions(
        top=1,
        max_characters=8000,
    ),
    max_cost=Money(
        amount="0.1000",
        currency="USD",
    ),
)

```
</dd>
</dl>
</dd>
</dl>

#### Parameters

<dl>
<dd>

<dl>
<dd>

**idempotency_key:** `typing.Optional[str]` 

One key per logical call, so a retry is never billed twice.

Optional on this operation; required on `upload_contents`, `fetch_contents_batch` and `search_batch`, where a duplicate would cost the most. The SDKs fill a fresh key when you give none and send the same key on every retry of that call. Give your own key when your program retries across processes, so the second run finds the first answer.

The form: 1 to 255 visible ASCII characters, used exactly as sent, so a value written as a quoted Structured Field String keeps its quotes as part of the key. That is a stated departure from the IETF draft `draft-ietf-httpapi-idempotency-key-header`, revision 08, which is not yet a standard; this parameter documents the form in full.

What a repeated key does:
- The same key with the same body returns the first answer again, with this call's `request_id`, `expires_at` as it stands and `replayed` true on every `cost`. Nothing is billed again.
- The same key while the first call still runs: `409 idempotency-key-in-flight`, with `Retry-After`.
- The same key with another body: `422 idempotency-key-reused`.

Answers are stored for 24 hours, per account, for billed answers and running jobs only; a free answer is not stored. A call that may bill is kept in the store from its start, so a second call with its key meets the `409` while it runs.
    
</dd>
</dl>

<dl>
<dd>

**query:** `typing.Optional[str]` — The question, 1 to 2,000 characters; required unless `subject_identifiers` is sent. `"phrase"`, `-word`, `OR`, one level of `( )`, `site:`, `filetype:`, `intitle:`, `inurl:`, `before:`, `after:` and `*` are honored where a source supports them, and the receipt's `operators_applied` says what each source did with each.
    
</dd>
</dl>

<dl>
<dd>

**alternate_queries:** `typing.Optional[typing.Sequence[str]]` — Other wordings of the question, in any language, each 1 to 2,000 characters, up to 10; one merged list with `query`, 20 wordings at most after OR splits. Default none. A wording runs only on the sources that cover its language; nothing is translated, so a wording in another language reaches the sources in that language. Without `query` it is refused `dependent`.
    
</dd>
</dl>

<dl>
<dd>

**subject_identifiers:** `typing.Optional[typing.Sequence[SubjectIdentifier]]` — Exact codes of the subject, up to 10 `SubjectIdentifier` objects; with no `query`, each identifier's value runs as a wording with origin `identifier`. `issuer` is required for `ticker`, `docket`, `tax_id` and `registry`, as the catalog's codes; a duplicate is refused `duplicate`. Default none.
    
</dd>
</dl>

<dl>
<dd>

**subject_country:** `typing.Optional[str]` — The country the search is made from, ISO 3166-1 alpha-2; groups of sources expand by it; the inline fetch reads from it when it is a country getclean can read from, one of `Limits.exits`, else from the key's `default_exit` with the notice `field_not_applicable`. Default none.
    
</dd>
</dl>

<dl>
<dd>

**purpose:** `typing.Optional[str]` — Your reason for the search, kept in the record and read by every model step; never sent to a source. At most 2,000 characters. Default none.
    
</dd>
</dl>

<dl>
<dd>

**datasources:** `typing.Optional[typing.Sequence[str]]` — Where to search: up to 10 of a datasource id, a group, or `set:NAME`, a published set, each 1 to 64 characters; these are names without dots, where `allowed_domains` takes site names with dots. When sent, the search runs on these plus the sources that resolve a scheme of your `subject_identifiers`, added without a model step, each in the receipt with reason `identifier`. When absent, it runs on `web` plus the groups a model chooses for the question, one model step, each named; under `deterministic_only`, on `web` only. An unknown id is `datasource-unknown`, an unknown set `domain-set-unknown`, a site name here `misplaced`.
    
</dd>
</dl>

<dl>
<dd>

**allowed_domains:** `typing.Optional[typing.Sequence[str]]` — Only results on these sites count, site names with dots: up to 500 of a domain, a wildcard such as `*.example.com`, a URL prefix, a suffix such as `.gov`, or `set:NAME`, a published set, each 1 to 2,048 characters. What each form reaches: a domain, that host and every host under it; `*.example.com`, the hosts under the domain and not the domain itself; a URL prefix, every address that begins with it; a suffix with a leading dot, every domain that ends in it; `set:NAME`, the sites of that set. It may narrow the key's `policy.allowed_domains` and never widen it, which is `policy-limit-exceeded`. Default none. A site in both this and `blocked_domains` is refused `exclusive`; a datasource id here `misplaced`.
    
</dd>
</dl>

<dl>
<dd>

**blocked_domains:** `typing.Optional[typing.Sequence[str]]` — Never results on these sites; up to 500 of the same forms and bound as `allowed_domains`, each form reaching what it reaches there. Default none.
    
</dd>
</dl>

<dl>
<dd>

**published_from:** `typing.Optional[datetime.date]` — Pages published on or after this date, inclusive, by the page's own date. Default none. With `published_within_days` it is refused `exclusive`; after `published_until` the pair is refused `order`; a date after today `bound`; a window that begins after `as_of_date` makes the notice `window_after_as_of_date`.
    
</dd>
</dl>

<dl>
<dd>

**published_until:** `typing.Optional[datetime.date]` — Pages published on or before this date, inclusive. Default none.
    
</dd>
</dl>

<dl>
<dd>

**published_within_days:** `typing.Optional[int]` — Pages published within this many days counted back from today, or from `as_of_date` when it is sent; 1 to 3,650. Not with `published_from` or `published_until`, which is refused `exclusive`. Default none.
    
</dd>
</dl>

<dl>
<dd>

**undated:** `typing.Optional[Undated]` — Whether pages with no detectable date are kept inside a date window: `shown` keeps them, `hidden` drops them. Default `shown`. Sent without a window it makes the notice `field_not_applicable`.
    
</dd>
</dl>

<dl>
<dd>

**languages:** `typing.Optional[typing.Sequence[str]]` — Only pages written in these languages, up to 10 BCP 47 tags, each 1 to 35 characters; what the pages are written in, independent of the wordings' languages. Default none.
    
</dd>
</dl>

<dl>
<dd>

**media_types:** `typing.Optional[typing.Sequence[str]]` — Only these file types, up to 10 IANA media types, each 1 to 255 characters; a bare `pdf` is refused `not_allowed` with `application/pdf` suggested. Default none.
    
</dd>
</dl>

<dl>
<dd>

**safe_search:** `typing.Optional[SafeSearch]` — How strictly adult content is filtered: `off`, `moderate` or `strict`. Where a source has the setting it is mapped to the nearest level, said with the notice `filter_emulated`; it never removes a source. Never looser than the key's `policy.safe_search`, which is `policy-limit-exceeded`. Default `moderate`.
    
</dd>
</dl>

<dl>
<dd>

**source_kinds:** `typing.Optional[typing.Sequence[str]]` — Only these kinds of publisher, 1 to 24 of `state`, `court`, `regulator`, `statistics_office`, `intergovernmental`, `standards_body`, `academic`, `scholarly_publisher`, `archive`, `reference`, `press`, `information_provider`, `company`, `professional_practice`, `trade_body`, `marketplace`, `civil_society`, `political`, `religious`, `education`, `healthcare`, `cultural`, `individual`, `community`, never `unknown`; a filter that removes, where `ranking_priorities` only reorders. Default none.
    
</dd>
</dl>

<dl>
<dd>

**source_independence:** `typing.Optional[SourceIndependence]` — Only sources independent of the subject, or only its own; `independent` or `self`. Needs a subject resolved from `subject_identifiers`, else the notice `field_not_applicable`. Default none, any.
    
</dd>
</dl>

<dl>
<dd>

**as_of_date:** `typing.Optional[datetime.date]` — Search each source as it stood at the end of that day, UTC, and read any inline fetch from an archive's copy of that day. A date not after today. Default none, the sources as they stand now. A source that keeps no history reports `no_history`.
    
</dd>
</dl>

<dl>
<dd>

**max_per_datasource:** `typing.Optional[int]` — Results taken from each source per wording, before merging; capped by the source's maximum. 1 to 100; default 10.
    
</dd>
</dl>

<dl>
<dd>

**ranking_instructions:** `typing.Optional[str]` — Your instructions to the ranking model, at most 2,000 characters; kept in the record. Default none. Refused `model-work-refused` under `deterministic_only`.
    
</dd>
</dl>

<dl>
<dd>

**ranking_priorities:** `typing.Optional[typing.Sequence[RankingPriority]]` — Source facts that go first, in this order, up to 4 of `official`, `independent`, `primary`, `reviewed`; the leads grouped by them, then ordered within each group by `ranking_order`. Default none. `independent` with no subject resolved makes the notice `field_not_applicable`.
    
</dd>
</dl>

<dl>
<dd>

**ranking_order:** `typing.Optional[RankingOrder]` — The order within each priority group; `relevance`, `newest` or `oldest`; undated pages last under the date orders; the relevance cut-off applies in every case. Default `relevance`.
    
</dd>
</dl>

<dl>
<dd>

**ranking_preferred_domains:** `typing.Optional[typing.Sequence[str]]` — Sites ranked first among results of equal relevance; other sites still count. Up to 500 of the forms of `allowed_domains`, each reaching what it reaches there, each 1 to 2,048 characters. Default none. A value outside `allowed_domains` when it is set, or in `blocked_domains`, is refused `dependent`.
    
</dd>
</dl>

<dl>
<dd>

**ranking_max_per_domain:** `typing.Optional[int]` — The most leads kept from one site in the answer, 1 to 50. Default none. With one allowed site it makes the notice `field_not_applicable`.
    
</dd>
</dl>

<dl>
<dd>

**max_candidates:** `typing.Optional[int]` — The leads returned, 1 to 50; default 10. The results past them are read free by `get_search`.
    
</dd>
</dl>

<dl>
<dd>

**max_excerpt_characters:** `typing.Optional[int]` — The excerpt per lead, in characters, 0 to 4,000; 0 means none. Default 600.
    
</dd>
</dl>

<dl>
<dd>

**max_total_characters:** `typing.Optional[int]` — The whole answer's text, excerpts and fetched pages together, 1,000 to 200,000; the excerpts first, cut from the last lead backwards when they alone pass it, then the fetched pages in rank order while they fit in what remains, a page that would pass it coming as `sections_only`; each cut the notice `total_characters_cut`. Default 40,000. Below `max_excerpt_characters` it is refused `order`.
    
</dd>
</dl>

<dl>
<dd>

**contents:** `typing.Optional[SearchContentsOptions]` — Fetch this many top leads in the same call, under the inline fetch's rules; `contents.max_characters` bounds one page, `max_total_characters` the whole answer. Default none. The options without `top` are refused `required`; `top` above `max_candidates` `order`; with `wait_seconds` below 5, the least a fetch needs, `order`.
    
</dd>
</dl>

<dl>
<dd>

**view:** `typing.Optional[View]` — How much of the record comes back: `full`, every member, or `compact`, the smaller form the `Search` schema lists. Default `full`.
    
</dd>
</dl>

<dl>
<dd>

**wait_seconds:** `typing.Optional[float]` — The most seconds this call may work, the ranking, the choice of sources and every inline fetch inside, counted from the start of the work; what did not finish comes back `partial`, named. 0.2 to 60; default 10.
    
</dd>
</dl>

<dl>
<dd>

**max_cost:** `typing.Optional[Money]` — The most this call may cost, in the account's currency. When it cannot cover everything, the extras are cut in order, each with the notice `cost_cut`: first each inline fetch's own extras, then whole fetches, then the ranking, then the choice of sources, then the results taken per source. Default the key's cap on one call. Below the smallest call's price, one `searches` and one `datasource_queries`, it is refused `cost-exceeds-cap` with `minimum_cap`.
    
</dd>
</dl>

<dl>
<dd>

**deterministic_only:** `typing.Optional[bool]` — Turn off every step a model judges: the ranking and the choice of sources, which the answer then says; the publisher's kind only from what getclean already knows; the inline fetch's `json_schema` and `summary` refused by name and its `highlights` found verbatim only. Text recognition on a scanned page fetched inline still runs and is listed. Default false. Sending false under a key whose policy forbids model work is `policy-limit-exceeded`.
    
</dd>
</dl>

<dl>
<dd>

**pinned_version:** `typing.Optional[str]` — The version of getclean to run under, at most 64 characters. Default the current version. A version not served is `version-withdrawn`.
    
</dd>
</dl>

<dl>
<dd>

**run_id:** `typing.Optional[str]` — The run the record belongs to, an existing run of the key. Default the key's default run. An unknown run is refused `not_allowed`.
    
</dd>
</dl>

<dl>
<dd>

**record_form:** `typing.Optional[str]` — Have the search written up for a reviewer: `plain`, in plain words, or `prisma`, in the PRISMA form a systematic review reports; an open set. Default none, no write-up.
    
</dd>
</dl>

<dl>
<dd>

**metadata:** `typing.Optional[typing.Dict[str, str]]` — Your own labels, returned on the record as sent and never passed to a source: at most 20 string pairs, keys of 1 to 64 characters, values of 1 to 512. Default none. An empty map is refused `bound`.
    
</dd>
</dl>

<dl>
<dd>

**max_source_price:** `typing.Optional[Money]` — The most you allow for a datasource that charges per query, or for a site an inline fetch meets that asks a price. A source whose fee passes it is not searched, the coverage gap `over_price`, never a refusal. getclean pays no site for a page, so a page that asks a price ends `payment_required`. Default none.
    
</dd>
</dl>

<dl>
<dd>

**retention:** `typing.Optional[Retention]` — How long the search record and every inline record are kept: `hold`, 48 hours after the last call and at most 30 days, allowed only under a `hold` policy; `none`, nothing kept past the answer. Default the key's `policy.retention`.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/getclean/client.py">get_search</a>(...) -> SyncPager[Candidate, Search]</code></summary>
<dl>
<dd>

#### Description

<dl>
<dd>

<dl>
<dd>

Read a search you already have, free: the first page as it was answered, and behind it the full list the search stored, including the results it dropped and why. Nothing is searched again and nothing is charged; only the record's `expires_at` moves.

The first page is the original answer as stored, whatever `page_size`: its members and the notices kept with it. A notice of the original answer that was not kept does not come back, and `dropped_reason` is absent on every candidate. A later page is the stored list in rank order, and every item on it carries `dropped_reason`. Every other member comes as stored; `request_id` is this call's, and `expires_at` is the record's new one. `next_page_token` comes while more remain. `fetch_contents` reads a candidate by its URL.

**What it costs.** The key needs `search:read`. The call is free. The answer is `200` with `Search`; the call moves the record's `expires_at` 48 hours ahead.

**Refused before any work.** A value outside its set or range, `page_size` above its maximum excepted, which is lowered with the notice `page_size_lowered`: `400 invalid-request`, `not_allowed` or `bound`, each with where it is. An id of the wrong kind: `400 invalid-request`, before any lookup. A token of another search or another query: `400 page-token-invalid`. An unknown query parameter: `400 invalid-request`, `unknown_field`.

**Notices this operation makes.** The search's own notices first, then `page_size_lowered` and `version_retiring`.

**Problem types.**
- 400 `invalid-request`, The request is invalid; `page-token-invalid`, The page token is invalid.
- 401 `unauthorized`, The key is missing or rejected.
- 403 `insufficient-scope`, The key lacks a scope this call needs.
- 404 `not-found`, Not found: an unknown or another account's search.
- 410 `search-expired`, The search has expired: for 30 days after it expired, to the owning account only, with `expired_at` and `change` naming `search`; then `404`.
- 429 `rate-limit-exceeded`, The rate limit is exceeded; `concurrency-limit-exceeded`, Too many calls are in flight.
- 500 `internal-error`, The service failed.
- 503 `overloaded`, The service is overloaded.
</dd>
</dl>
</dd>
</dl>

#### Usage

<dl>
<dd>

<dl>
<dd>

```python
from getclean import GetClean
from getclean.environment import GetCleanEnvironment

client = GetClean(
    environment=GetCleanEnvironment.PRODUCTION,
)

client.get_search(
    search_id="srch_4HmUunqCCXquleKVCosqFG",
    page_token="eyJzIjoic3JjaF80SG0iLCJvIjoyfQ",
)

```
</dd>
</dl>
</dd>
</dl>

#### Parameters

<dl>
<dd>

<dl>
<dd>

**search_id:** `str` — The search record, an `srch_` id as `search` returned it.
    
</dd>
</dl>

<dl>
<dd>

**view:** `typing.Optional[View]` — How much of the record comes back: `full`, every member, or `compact`, the smaller form the `Search` schema lists. Default `full`.
    
</dd>
</dl>

<dl>
<dd>

**page_size:** `typing.Optional[int]` — Results per page of the stored list, from 1; the maximum, 50, stands in `Limits.bounds`, and a larger value is lowered with the notice `page_size_lowered`. Default the search's `max_candidates`.
    
</dd>
</dl>

<dl>
<dd>

**page_token:** `typing.Optional[str]` — The next page of the stored list, as the last answer's `next_page_token` gave it; opaque, at most 1,024 characters, alive as long as the record. Default none, the first page.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/getclean/client.py">search_batch</a>(...) -> SearchBatch</code></summary>
<dl>
<dd>

#### Description

<dl>
<dd>

<dl>
<dd>

Run 1 to 20 searches in one call, one record each. You get the tally first, then one result per item in input order, each a search record or the problem that skipped it; nothing is atomic, so a skipped item leaves the others standing. Each item carries its own question, wordings, identifiers, country and purpose; every other field of `search` stands once at the top and is shared by every item.

**What it costs.** The key needs `search:run`. The price is the sum of the searches' costs, `units` summed by name. The answer is `200` with `SearchBatch`. The body is at most 4 MiB.

**The idempotency key.** `Idempotency-Key` is required here, since a repeated batch would run and bill every search twice; its absence is `400 invalid-request` naming the header. A replay repeats the whole answer with this call's `request_id`, the current `expires_at` of every record and `replayed` true on every `cost`; the same key in flight is `409 idempotency-key-in-flight`; the same key with another body `422 idempotency-key-reused`.

**Faults and limits.**
- A datasource behind an unregistered login, a policy the item's sites break, a legal demand, or the remainder of the ceiling: that item comes back `skipped` with its problem, without `status`, and the batch still runs. A fault of a shared top field skips every item. A fault of the batch's shape or of any field's rule refuses the whole call.
- `wait_seconds` is each item's own deadline from its own start. The call's whole time is bounded by `bounds.search.batch_seconds`, and an item not started when it ends is `skipped` with the problem `overloaded`, `retry_after_seconds` set.
- `max_cost`: the whole call is refused below one search's smallest price, with the problem of the limit that binds; else it is reserved at the start and split in input order, each item its smallest call and the model steps asked by name. The items the remainder cannot cover are `skipped` with the problem of the limit that binds: `cost-exceeds-cap` for the request's `max_cost`, `policy-limit-exceeded` for the key's cap, `credit-exhausted`, `run-budget-exhausted` or `key-budget-exhausted`.
- An item's `Search` carries the batch call's `request_id`, its `applied_request` the item's fields merged with the top's, the top's `metadata`, and its own `expires_at`.

**Refused before any work**, every violation of the body reported at once in `violations`:
- Fewer than 1 or more than 20 items: `invalid-field`, `bound`.
- An item with neither `query` nor `subject_identifiers`: `required`.
- A `label` repeated: `duplicate`; a `label` outside its character set or length: `syntax`, `bound`.
- A top-only field inside an item, or an item field at the top: `misplaced`.
- Every rule of `search` on the top fields and on an item's own fields refuses the whole call, except a named source behind a login the key has not registered, a site the key's policy forbids and a legal block, which skip the items they touch.
- An unknown field, at the top or in an item: `unknown_field`.
- `Idempotency-Key` absent: `400 invalid-request`.

**Notices this operation makes.** Every notice of `search` inside each item's record, `version_retiring` inside each too.

**Problem types.** For the whole call:
- 400 `invalid-request`, The request is invalid.
- 401 `unauthorized`, The key is missing or rejected.
- 403 `insufficient-scope`, The key lacks a scope this call needs; `policy-limit-exceeded`, The key's policy forbids this, for a setting, a minimum or a widening of the key's domain policy; `credit-exhausted`, The credit is exhausted; `run-budget-exhausted`, The run's budget is exhausted; `key-budget-exhausted`, The key's budget is exhausted.
- 409 `idempotency-key-in-flight`, The same request is still running.
- 413 `body-too-large`, The body is too large.
- 415 `unsupported-media-type`, The media type is not supported.
- 422 `invalid-field`, A field is invalid; `model-work-refused`, Model work is refused by the request; `cost-exceeds-cap`, The cost cap is below the smallest call; `version-withdrawn`, The version is no longer served; `idempotency-key-reused`, The idempotency key was reused with another body; `no-datasource-can-run`, No datasource can run this search; `datasource-unknown`, The datasource is unknown; `datasource-not-searchable`, The datasource has no search; `domain-set-unknown`, The domain set is unknown.
- 429 `rate-limit-exceeded`, The rate limit is exceeded; `concurrency-limit-exceeded`, Too many calls are in flight.
- 500 `internal-error`, The service failed.
- 503 `overloaded`, The service is overloaded.

Inside a skipped item, each without `status`: `datasource-access-required`, `policy-limit-exceeded`, `legal-block`, `cost-exceeds-cap`, `credit-exhausted`, `run-budget-exhausted`, `key-budget-exhausted`, `overloaded`.
</dd>
</dl>
</dd>
</dl>

#### Usage

<dl>
<dd>

<dl>
<dd>

```python
from getclean import GetClean, SearchBatchItem, Money
from getclean.environment import GetCleanEnvironment

client = GetClean(
    environment=GetCleanEnvironment.PRODUCTION,
)

client.search_batch(
    items=[
        SearchBatchItem(
            label="a",
            query="EU AI Act article 50 marking obligations",
        ),
        SearchBatchItem(
            label="b",
            query="EU AI Act article 52 transparency",
        )
    ],
    max_candidates=3,
    max_cost=Money(
        amount="0.0150",
        currency="USD",
    ),
)

```
</dd>
</dl>
</dd>
</dl>

#### Parameters

<dl>
<dd>

<dl>
<dd>

**items:** `typing.Sequence[SearchBatchItem]` — The searches, 1 to 20 `SearchBatchItem` objects in the order the results come back; the same question may repeat and makes two records. Required.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `typing.Optional[str]` 

One key per logical call, so a retry is never billed twice.

Required on this operation, where a duplicate would cost the most; without it the call is `400 invalid-request` naming the header. The SDKs fill a fresh key when you give none and send the same key on every retry of that call. Give your own key when your program retries across processes, so the second run finds the first answer.

The form: 1 to 255 visible ASCII characters, used exactly as sent, so a value written as a quoted Structured Field String keeps its quotes as part of the key. That is a stated departure from the IETF draft `draft-ietf-httpapi-idempotency-key-header`, revision 08, which is not yet a standard; this parameter documents the form in full.

What a repeated key does:
- The same key with the same body returns the first answer again, with this call's `request_id`, the current `expires_at` and `replayed` true on every `cost`. Nothing is billed again. On the upload the body is compared by a digest over the document and the fields, and a retried start with the same key is the same job.
- The same key while the first call still runs: `409 idempotency-key-in-flight`, with `Retry-After`.
- The same key with another body: `422 idempotency-key-reused`.

Answers are stored for 24 hours, per account, for billed answers and running jobs only. A call that may bill is kept in the store from its start, so a second call with its key meets the `409` while it runs.
    
</dd>
</dl>

<dl>
<dd>

**datasources:** `typing.Optional[typing.Sequence[str]]` — Where to search: up to 10 of a datasource id, a group, or `set:NAME`, a published set, each 1 to 64 characters; these are names without dots, where `allowed_domains` takes site names with dots. When sent, the search runs on these plus the sources that resolve a scheme of your `subject_identifiers`, added without a model step, each in the receipt with reason `identifier`. When absent, it runs on `web` plus the groups a model chooses for the question, one model step, each named; under `deterministic_only`, on `web` only. An unknown id is `datasource-unknown`, an unknown set `domain-set-unknown`, a site name here `misplaced`.
    
</dd>
</dl>

<dl>
<dd>

**allowed_domains:** `typing.Optional[typing.Sequence[str]]` — Only results on these sites count, site names with dots: up to 500 of a domain, a wildcard such as `*.example.com`, a URL prefix, a suffix such as `.gov`, or `set:NAME`, a published set, each 1 to 2,048 characters. What each form reaches: a domain, that host and every host under it; `*.example.com`, the hosts under the domain and not the domain itself; a URL prefix, every address that begins with it; a suffix with a leading dot, every domain that ends in it; `set:NAME`, the sites of that set. It may narrow the key's `policy.allowed_domains` and never widen it, which is `policy-limit-exceeded`. Default none. A site in both this and `blocked_domains` is refused `exclusive`; a datasource id here `misplaced`.
    
</dd>
</dl>

<dl>
<dd>

**blocked_domains:** `typing.Optional[typing.Sequence[str]]` — Never results on these sites; up to 500 of the same forms and bound as `allowed_domains`, each form reaching what it reaches there. Default none.
    
</dd>
</dl>

<dl>
<dd>

**published_from:** `typing.Optional[datetime.date]` — Pages published on or after this date, inclusive, by the page's own date. Default none. With `published_within_days` it is refused `exclusive`; after `published_until` the pair is refused `order`; a date after today `bound`; a window that begins after `as_of_date` makes the notice `window_after_as_of_date`.
    
</dd>
</dl>

<dl>
<dd>

**published_until:** `typing.Optional[datetime.date]` — Pages published on or before this date, inclusive. Default none.
    
</dd>
</dl>

<dl>
<dd>

**published_within_days:** `typing.Optional[int]` — Pages published within this many days counted back from today, or from `as_of_date` when it is sent; 1 to 3,650. Not with `published_from` or `published_until`, which is refused `exclusive`. Default none.
    
</dd>
</dl>

<dl>
<dd>

**undated:** `typing.Optional[Undated]` — Whether pages with no detectable date are kept inside a date window: `shown` keeps them, `hidden` drops them. Default `shown`. Sent without a window it makes the notice `field_not_applicable`.
    
</dd>
</dl>

<dl>
<dd>

**languages:** `typing.Optional[typing.Sequence[str]]` — Only pages written in these languages, up to 10 BCP 47 tags, each 1 to 35 characters; what the pages are written in, independent of the wordings' languages. Default none.
    
</dd>
</dl>

<dl>
<dd>

**media_types:** `typing.Optional[typing.Sequence[str]]` — Only these file types, up to 10 IANA media types, each 1 to 255 characters; a bare `pdf` is refused `not_allowed` with `application/pdf` suggested. Default none.
    
</dd>
</dl>

<dl>
<dd>

**safe_search:** `typing.Optional[SafeSearch]` — How strictly adult content is filtered: `off`, `moderate` or `strict`. Where a source has the setting it is mapped to the nearest level, said with the notice `filter_emulated`; it never removes a source. Never looser than the key's `policy.safe_search`, which is `policy-limit-exceeded`. Default `moderate`.
    
</dd>
</dl>

<dl>
<dd>

**source_kinds:** `typing.Optional[typing.Sequence[str]]` — Only these kinds of publisher, 1 to 24 of `state`, `court`, `regulator`, `statistics_office`, `intergovernmental`, `standards_body`, `academic`, `scholarly_publisher`, `archive`, `reference`, `press`, `information_provider`, `company`, `professional_practice`, `trade_body`, `marketplace`, `civil_society`, `political`, `religious`, `education`, `healthcare`, `cultural`, `individual`, `community`, never `unknown`; a filter that removes, where `ranking_priorities` only reorders. Default none.
    
</dd>
</dl>

<dl>
<dd>

**source_independence:** `typing.Optional[SourceIndependence]` — Only sources independent of the subject, or only its own; `independent` or `self`. Needs a subject resolved from an item's `subject_identifiers`, else the notice `field_not_applicable`. Default none, any.
    
</dd>
</dl>

<dl>
<dd>

**as_of_date:** `typing.Optional[datetime.date]` — Search each source as it stood at the end of that day, UTC, and read any inline fetch from an archive's copy of that day. A date not after today. Default none, the sources as they stand now. A source that keeps no history reports `no_history`.
    
</dd>
</dl>

<dl>
<dd>

**max_per_datasource:** `typing.Optional[int]` — Results taken from each source per wording, before merging; capped by the source's maximum. 1 to 100; default 10.
    
</dd>
</dl>

<dl>
<dd>

**ranking_instructions:** `typing.Optional[str]` — Your instructions to the ranking model, at most 2,000 characters; kept in the record. Default none. Refused `model-work-refused` under `deterministic_only`.
    
</dd>
</dl>

<dl>
<dd>

**ranking_priorities:** `typing.Optional[typing.Sequence[RankingPriority]]` — Source facts that go first, in this order, up to 4 of `official`, `independent`, `primary`, `reviewed`; the leads grouped by them, then ordered within each group by `ranking_order`. Default none. `independent` with no subject resolved makes the notice `field_not_applicable`.
    
</dd>
</dl>

<dl>
<dd>

**ranking_order:** `typing.Optional[RankingOrder]` — The order within each priority group; `relevance`, `newest` or `oldest`; undated pages last under the date orders; the relevance cut-off applies in every case. Default `relevance`.
    
</dd>
</dl>

<dl>
<dd>

**ranking_preferred_domains:** `typing.Optional[typing.Sequence[str]]` — Sites ranked first among results of equal relevance; other sites still count. Up to 500 of the forms of `allowed_domains`, each reaching what it reaches there, each 1 to 2,048 characters. Default none. A value outside `allowed_domains` when it is set, or in `blocked_domains`, is refused `dependent`.
    
</dd>
</dl>

<dl>
<dd>

**ranking_max_per_domain:** `typing.Optional[int]` — The most leads kept from one site in the answer, 1 to 50. Default none. With one allowed site it makes the notice `field_not_applicable`.
    
</dd>
</dl>

<dl>
<dd>

**max_candidates:** `typing.Optional[int]` — The leads returned per search, 1 to 50; default 10. The results past them are read free by `get_search`.
    
</dd>
</dl>

<dl>
<dd>

**max_excerpt_characters:** `typing.Optional[int]` — The excerpt per lead, in characters, 0 to 4,000; 0 means none. Default 600.
    
</dd>
</dl>

<dl>
<dd>

**max_total_characters:** `typing.Optional[int]` — Each search's whole text, excerpts and fetched pages together, 1,000 to 200,000; the excerpts first, cut from the last lead backwards when they alone pass it, then the fetched pages in rank order while they fit in what remains, a page that would pass it coming as `sections_only`; each cut the notice `total_characters_cut`. Default 40,000. Below `max_excerpt_characters` it is refused `order`.
    
</dd>
</dl>

<dl>
<dd>

**contents:** `typing.Optional[SearchContentsOptions]` — Fetch this many top leads of each search in the same call, under the inline fetch's rules; `contents.max_characters` bounds one page, `max_total_characters` the whole answer. Default none. The options without `top` are refused `required`; `top` above `max_candidates` `order`; with `wait_seconds` below 5, the least a fetch needs, `order`.
    
</dd>
</dl>

<dl>
<dd>

**view:** `typing.Optional[View]` — How much of each record comes back: `full`, every member, or `compact`, the smaller form the `Search` schema lists. Default `full`.
    
</dd>
</dl>

<dl>
<dd>

**wait_seconds:** `typing.Optional[float]` — The most seconds each search may work, counted from its own start, the ranking, the choice of sources and every inline fetch inside; the call's whole time is bounded by `bounds.search.batch_seconds`. 0.2 to 60; default 10.
    
</dd>
</dl>

<dl>
<dd>

**max_cost:** `typing.Optional[Money]` — The most the whole call may cost, in the account's currency; reserved at the start and split in input order, each item its smallest call and the model steps asked by name, the items the remainder cannot cover skipped. Default the key's cap on one call. Below one search's smallest price, one `searches` and one `datasource_queries`, it is refused with the problem of the limit that binds, `cost-exceeds-cap` with `minimum_cap` for the request's own.
    
</dd>
</dl>

<dl>
<dd>

**deterministic_only:** `typing.Optional[bool]` — Turn off, for every search, every step a model judges: the ranking and the choice of sources, which the answer then says; the publisher's kind only from what getclean already knows; the inline fetch's `json_schema` and `summary` refused by name and its `highlights` found verbatim only. Default false. Sending false under a key whose policy forbids model work is `policy-limit-exceeded`.
    
</dd>
</dl>

<dl>
<dd>

**pinned_version:** `typing.Optional[str]` — The version of getclean to run under, at most 64 characters. Default the current version. A version not served is `version-withdrawn`.
    
</dd>
</dl>

<dl>
<dd>

**run_id:** `typing.Optional[str]` — The run every record belongs to, an existing run of the key. Default the key's default run. An unknown run is refused `not_allowed`.
    
</dd>
</dl>

<dl>
<dd>

**record_form:** `typing.Optional[str]` — Have each search written up for a reviewer: `plain`, in plain words, or `prisma`, in the PRISMA form a systematic review reports; an open set. Default none, no write-up.
    
</dd>
</dl>

<dl>
<dd>

**metadata:** `typing.Optional[typing.Dict[str, str]]` — Your own labels, returned on every search record as sent and never passed to a source: at most 20 string pairs, keys of 1 to 64 characters, values of 1 to 512. Default none. An empty map is refused `bound`.
    
</dd>
</dl>

<dl>
<dd>

**max_source_price:** `typing.Optional[Money]` — The most you allow for a datasource that charges per query, or for a site an inline fetch meets that asks a price. A source whose fee passes it is not searched, the coverage gap `over_price`, never a refusal. getclean pays no site for a page, so a page that asks a price ends `payment_required`. Default none.
    
</dd>
</dl>

<dl>
<dd>

**retention:** `typing.Optional[Retention]` — How long every search record and inline record of the batch is kept: `hold`, 48 hours after the last call and at most 30 days, allowed only under a `hold` policy; `none`, nothing kept past the answer. Default the key's `policy.retention`.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/getclean/client.py">list_datasources</a>(...) -> SyncPager[Datasource, DatasourcePage]</code></summary>
<dl>
<dd>

#### Description

<dl>
<dd>

<dl>
<dd>

List the places getclean can search, free; the answer may be cached for an hour. An entry's `id`, its `group` or `set:NAME` goes into the search's `datasources`; `filters` and `operators` say what each source honors, before any search; `issuers` gives the codes an identifier scheme takes, so your agent learns a code from the catalog and never guesses one. Every filter you send must match, and the order is the catalog's own.

**What it costs.** The key needs `search:read`. The call is free. The answer is `200` with `DatasourcePage` and `Cache-Control: max-age=3600`, so a cached answer repeats the first call's `request_id` and rate figures, which describe that call and not yours.

**Paging.** `page_size` from 1, default 50, maximum 200, a larger value lowered with the notice `page_size_lowered`; `page_token` is opaque, bound to its query, alive 24 hours; `next_page_token` is absent on the last page, and a page that carries it holds at least one entry.

**Refused before any work.** A value outside its set or range, `page_size` above its maximum excepted, which is lowered: `400 invalid-request`, `not_allowed` or `bound`, each with where it is. A token of another list: `400 page-token-invalid`. An unknown query parameter: `400 invalid-request`, `unknown_field`.

**Notices this operation makes.** `page_size_lowered`.

**Problem types.**
- 400 `invalid-request`, The request is invalid; `page-token-invalid`, The page token is invalid.
- 401 `unauthorized`, The key is missing or rejected.
- 403 `insufficient-scope`, The key lacks a scope this call needs.
- 429 `rate-limit-exceeded`, The rate limit is exceeded; `concurrency-limit-exceeded`, Too many calls are in flight.
- 500 `internal-error`, The service failed.
- 503 `overloaded`, The service is overloaded.
</dd>
</dl>
</dd>
</dl>

#### Usage

<dl>
<dd>

<dl>
<dd>

```python
from getclean import GetClean
from getclean.environment import GetCleanEnvironment

client = GetClean(
    environment=GetCleanEnvironment.PRODUCTION,
)

client.list_datasources(
    country="US",
    language="en",
    access="open",
)

```
</dd>
</dl>
</dd>
</dl>

#### Parameters

<dl>
<dd>

<dl>
<dd>

**group:** `typing.Optional[str]` — Only this group, `web` or a group the catalog publishes, an open set, 1 to 64 characters. Default none.
    
</dd>
</dl>

<dl>
<dd>

**country:** `typing.Optional[str]` — Only sources that cover this country, ISO 3166-1 alpha-2. Default none.
    
</dd>
</dl>

<dl>
<dd>

**language:** `typing.Optional[str]` — Only sources that cover this language, BCP 47, 1 to 35 characters. Default none.
    
</dd>
</dl>

<dl>
<dd>

**access:** `typing.Optional[str]` — Only sources reached this way: `open`, no login; `registered`, a login the account owner registers; `paid`, a fee per query. An open set. Default none.
    
</dd>
</dl>

<dl>
<dd>

**page_size:** `typing.Optional[int]` — At most this many entries on the page, from 1; default 50; the maximum, 200, stands in `Limits.bounds`, and a larger value is lowered with the notice `page_size_lowered`.
    
</dd>
</dl>

<dl>
<dd>

**page_token:** `typing.Optional[str]` — The next page, as the last answer's `next_page_token` gave it; opaque, at most 1,024 characters, never built by the caller. Default none, the first page.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.<a href="src/getclean/client.py">get_datasource</a>(...) -> Datasource</code></summary>
<dl>
<dd>

#### Description

<dl>
<dd>

<dl>
<dd>

Read one entry of the catalog whole, free; the answer may be cached for an hour. You get what the source covers, how it is reached, which filters and operators it honors, which identifier schemes it resolves and with which issuer codes, and whether it keeps history for `as_of_date`.

**What it costs.** The key needs `search:read`. The call is free. The answer is `200` with `Datasource` and `Cache-Control: max-age=3600`.

**Refused before any work.** An id of the wrong form, other than 1 to 64 of `a-z`, `0-9` and `_` with a letter first: `400 invalid-request`, `syntax`, before any lookup. An unknown query parameter: `400 invalid-request`, `unknown_field`.

**Problem types.**
- 400 `invalid-request`, The request is invalid.
- 401 `unauthorized`, The key is missing or rejected.
- 403 `insufficient-scope`, The key lacks a scope this call needs.
- 404 `not-found`, Not found: no entry has this id.
- 429 `rate-limit-exceeded`, The rate limit is exceeded; `concurrency-limit-exceeded`, Too many calls are in flight.
- 500 `internal-error`, The service failed.
- 503 `overloaded`, The service is overloaded.
</dd>
</dl>
</dd>
</dl>

#### Usage

<dl>
<dd>

<dl>
<dd>

```python
from getclean import GetClean
from getclean.environment import GetCleanEnvironment

client = GetClean(
    environment=GetCleanEnvironment.PRODUCTION,
)

client.get_datasource(
    datasource_id="courtlistener",
)

```
</dd>
</dl>
</dd>
</dl>

#### Parameters

<dl>
<dd>

<dl>
<dd>

**datasource_id:** `str` — The catalog's id, 1 to 64 of `a-z`, `0-9` and `_`, a letter first, as `web` and `courtlistener`.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

