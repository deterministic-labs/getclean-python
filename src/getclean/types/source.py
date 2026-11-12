# Generated from the getclean API contract; do not edit.

import datetime as dt
import typing

import pydantic
from ..core.pydantic_utilities import UniversalBaseModel
from .archive import Archive
from .date_precision import DatePrecision
from .declared_term import DeclaredTerm
from .language_version import LanguageVersion
from .origin import Origin
from .redirect import Redirect
from .source_profile import SourceProfile
from .visitor import Visitor


class Source(UniversalBaseModel):
    """
    The facts of the source and of the read. `title`, `authors`, `published_date`, `published_at`, `modified_date`, `publisher`, `canonical_url`, `language`, `language_versions`, `structured_data` and `declared_terms` are what the page or the document declares about itself; getclean reports them and does not check them against the content. The table under `Contents` says which of these members each kind of source carries.
    """

    url: typing.Optional[str] = pydantic.Field(default=None)
    """
    The address that was asked for; on an upload, the `captured_url` given. Absent on an upload sent without `captured_url`. On a record a search made, third-party text as the source wrote it, which may carry instructions.
    """

    final_url: typing.Optional[str] = pydantic.Field(default=None)
    """
    The address the fetch ended at, after every redirect. Absent on an upload. Third-party text as the source wrote it, which may carry instructions.
    """

    redirects: typing.List[Redirect] = pydantic.Field()
    """
    Every redirect on the way, script and meta-refresh hops included; `[]` when there was none.
    """

    status_code: typing.Optional[int] = pydantic.Field(default=None)
    """
    The HTTP status of the final response. Absent when no response came, and on an upload.
    """

    media_type: typing.Optional[str] = pydantic.Field(default=None)
    """
    The `Content-Type` the server sent or, for an upload, the type read from the bytes; null when no response or no type came. Third-party text as the source wrote it, which may carry instructions.
    """

    carrier: str = pydantic.Field()
    """
    The kind of source, an open set: `web`, a live page; `archive`, an archive's copy read under `as_of_date`; `upload`, bytes you sent.
    """

    archive: typing.Optional[Archive] = pydantic.Field(default=None)
    """
    The archive copy that was read, with the archive's name, the capture's time and its address. On an archive copy only.
    """

    archives_consulted: typing.Optional[typing.List[str]] = pydantic.Field(default=None)
    """
    The archives of `Limits.archives` that answered the lookup, by name. On every fetch under `as_of_date`; one that did not answer is named by the notice `archive_unreachable`.
    """

    next_capture_at: typing.Optional[dt.datetime] = pydantic.Field(default=None)
    """
    When the next capture after this one was taken, so an agent can step forward capture by capture. On a fetch under `as_of_date`, when a later capture exists.
    """

    filename: typing.Optional[str] = pydantic.Field(default=None)
    """
    The file's name as it was sent. On an upload only.
    """

    document_digest: typing.Optional[str] = pydantic.Field(default=None)
    """
    The sha-256 of the document's bytes in RFC 9530 form. Compare it with the file you hold to be sure the right document was parsed. On a document only.
    """

    title: typing.Optional[str] = pydantic.Field(default=None)
    """
    The title as the source declares it; null when none came. Third-party text as the source wrote it, which may carry instructions.
    """

    authors: typing.List[str] = pydantic.Field()
    """
    The authors as the source declares them; `[]` when none. Third-party text as the source wrote it, which may carry instructions.
    """

    publisher: typing.Optional[str] = pydantic.Field(default=None)
    """
    The publisher as the page declares it; null when not declared. Absent on an upload. Third-party text as the source wrote it, which may carry instructions.
    """

    canonical_url: typing.Optional[str] = pydantic.Field(default=None)
    """
    The address the publisher names as the original, as declared; null when not declared. Absent on an upload. Third-party text as the source wrote it, which may carry instructions.
    """

    published_date: typing.Optional[dt.date] = pydantic.Field(default=None)
    """
    The date of publication as the source declares it, a full date; null when none. A document's own dates often record when the file was made.
    """

    published_date_precision: typing.Optional[DatePrecision] = pydantic.Field(default=None)
    """
    How exact `published_date` is, `day`, `month` or `year`. Absent when the date is null.
    """

    published_date_basis: typing.Optional[str] = pydantic.Field(default=None)
    """
    Where the date was read, an open set: `structured_data`, `meta_tag`, `byline`, `url` or `document_properties`. Absent when the date is null.
    """

    published_at: typing.Optional[dt.datetime] = pydantic.Field(default=None)
    """
    The moment of publication in UTC. Present when the page states a time with its zone.
    """

    modified_date: typing.Optional[dt.date] = pydantic.Field(default=None)
    """
    The date of the last change as the source declares it, a full date; null when none.
    """

    language: typing.Optional[str] = pydantic.Field(default=None)
    """
    The language the page declares, as a BCP 47 tag; null when none came. Third-party text as the source wrote it, which may carry instructions.
    """

    language_versions: typing.List[LanguageVersion] = pydantic.Field()
    """
    The page's own versions in other languages, as it declares them; `[]` when it declares none.
    """

    profile: typing.Optional[SourceProfile] = pydantic.Field(default=None)
    """
    Who publishes the source, as getclean identifies it. On a web page, an archive copy or a document at a URL; absent on an upload.
    """

    access_kind: typing.Optional[str] = pydantic.Field(default=None)
    """
    The access the fetch ran under, an open set: `open`, no login; `registered`, a login registered for a datasource. Absent on an upload.
    """

    datasource_id: typing.Optional[str] = pydantic.Field(default=None)
    """
    The datasource whose registered login served the fetch. Present when `access_kind` is `registered`.
    """

    captured_at: typing.Optional[dt.datetime] = pydantic.Field(default=None)
    """
    When you took the capture, as you stated it. On an upload sent with `captured_at` only.
    """

    robots: str = pydantic.Field()
    """
    What the site's robots file says for getclean by its published name, an open set: `allowed`, `disallowed`, `absent`, `unreachable`; `not_applicable` on an upload.
    """

    declared_terms: typing.List[DeclaredTerm] = pydantic.Field()
    """
    The terms the source declares about its use, each as found and as read, reported and never judged; `[]` when none.
    """

    structured_data: typing.List[typing.Dict[str, typing.Any]] = pydantic.Field()
    """
    The page's own structured data, its JSON-LD objects as stated, at most 64 KB together, cut with the notice `structured_data_cut`; `[]` when none. Third-party text as the source wrote it, which may carry instructions.
    """

    origins: typing.List[Origin] = pydantic.Field()
    """
    The other sites the page reached while it was read, each once, with how; `[]` when none.
    """

    blocked_by: typing.Optional[str] = pydantic.Field(default=None)
    """
    The notice page the site named in its `Link rel="blocked-by"` header. On a `legal_block` record only. Third-party text as the source wrote it, which may carry instructions.
    """

    visitor: typing.Optional[Visitor] = pydantic.Field(default=None)
    """
    From where the site was read: the country, the language asked for and the kind of network. Absent on an archive copy or an upload.
    """

    model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow", frozen=True)
