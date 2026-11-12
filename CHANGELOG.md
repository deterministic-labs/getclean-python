# Changelog

Every notable change to `getclean`, newest first. The format follows Keep a Changelog, and the version numbers follow semantic versioning. Each entry names the version of the getclean API contract the package was generated from.

## Unreleased

The first release of getclean for Python, built against the getclean API contract 1.0.3.

### Added

- The client `GetClean` and its async twin `AsyncGetClean`, with every one of the API's 22 operations: fetch a page or a document as a record and read it again for free by its sections, blocks and links; upload a document and wait for its record; fetch and search in batches; search the web and specialist sources and read a search again; find words or questions in a record, fill a JSON schema or summarize a record; compare two records; list, read and delete records; list, read and cancel jobs; read the catalog of sources and your limits.
- One idempotency key per call that may bill, filled by the SDK when you give none, kept on every retry and carried on the error when the call fails, so your own repeat is a replay and never a second charge.
- Retries of `429`, `502`, `503` and `504`, and of a `409` whose key is still in flight, under one count of five attempts with a backoff that never passes 30 seconds; a `Retry-After` within that cap is waited as sent, and a longer one ends the retries with the answer returned to you.
- A timeout per attempt taken from the API's published bounds for each call that may bill, 120 seconds until the limits have been read and for every other call; your own timeout, on the call or on the client, always stands.
- `upload_contents(document="minutes.pdf", wait=True)`, which follows the job and returns the record; `iter_section`, which pages through a long section; pagers for jobs and records that leave out an item repeated across pages.
- One typed error per status, each carrying the problem the API sent, and `JobCanceled` for a job canceled before any record exists.
- `GETCLEAN_API_KEY` and `GETCLEAN_BASE_URL` read from the environment when you give no key or no host.
