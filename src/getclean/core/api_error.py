# Part of the generated SDK of the getclean API; do not edit.

from typing import Any, Dict, Mapping, Optional


class ApiError(Exception):
    headers: Optional[Dict[str, str]]
    status_code: Optional[int]
    body: Any

    def __init__(
        self,
        *,
        headers: Optional[Dict[str, str]] = None,
        status_code: Optional[int] = None,
        body: Any = None,
    ) -> None:
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def __str__(self) -> str:
        details = f"headers: {self.headers}, status_code: {self.status_code}, body: {self.body}"
        description = _problem_description(self.body)
        return f"{description} ({details})" if description else details


def _problem_description(body: Any) -> Optional[str]:
    """The problem the body states, when it states one: its `title` and `detail` as "title: detail", or the one given.

    The body is the parsed error type of a declared error, or the response's JSON or text when none is declared. A
    text, a list, or a body without those members as non-empty text gives None, and the message keeps the headers,
    the status and the body alone.
    """
    if isinstance(body, Mapping):
        values = (body.get("title"), body.get("detail"))
    elif body is None or isinstance(body, (str, bytes, list, tuple)):
        return None
    else:
        values = (getattr(body, "title", None), getattr(body, "detail", None))
    parts = [value.strip() for value in values if isinstance(value, str) and value.strip()]
    return ": ".join(parts) if parts else None
