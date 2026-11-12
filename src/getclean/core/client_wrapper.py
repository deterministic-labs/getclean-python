# Generated from the getclean API contract; do not edit.

import typing

import httpx
from .http_client import AsyncHttpClient, HttpClient
from .logging import LogConfig, Logger


def _append_app_info_to_user_agent(user_agent: str, app_info: typing.Optional[typing.Dict[str, str]]) -> str:
    if app_info is None:
        return user_agent

    def _percent_encode_char(char: str) -> str:
        return "".join(f"%{byte:02X}" for byte in char.encode("utf-8"))

    # RFC 7230 token = 1*tchar. Any character outside that set is percent-encoded so it
    # cannot break out of the product token or inject additional header content.
    _tchar = "!#$%&'*+-.^_`|~0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

    def _encode_token(value: str) -> str:
        return "".join(c if c in _tchar else _percent_encode_char(c) for c in value)

    # Escape the comment delimiters `(`, `)`, `\` and control characters (0x00-0x1F,
    # 0x7F, incl. CR/LF), and percent-encode any non-ASCII byte (>= 0x80) so a
    # caller-supplied comment cannot terminate the comment group early, inject additional
    # header content, or raise a UnicodeEncodeError when httpx ASCII-encodes the header.
    def _encode_comment(value: str) -> str:
        return "".join(_percent_encode_char(c) if c in "()\\" or ord(c) < 0x20 or ord(c) >= 0x7F else c for c in value)

    name = _encode_token((app_info.get("name") or "").strip())
    if not name:
        return user_agent
    product_token = name
    version = _encode_token((app_info.get("version") or "").strip())
    if version:
        product_token += f"/{version}"
    comment = _encode_comment((app_info.get("comment") or "").strip())
    if comment:
        product_token += f" ({comment})"
    return f"{user_agent} {product_token}"


class BaseClientWrapper:
    def __init__(
        self,
        *,
        api_key: typing.Optional[typing.Union[str, typing.Callable[[], str]]] = None,
        headers: typing.Optional[typing.Dict[str, str]] = None,
        app_info: typing.Optional[typing.Dict[str, str]] = None,
        base_url: str,
        timeout: typing.Optional[float] = None,
        max_retries: int = 4,
        logging: typing.Optional[typing.Union[LogConfig, Logger]] = None,
    ):
        self._api_key = api_key
        self._headers = headers
        self._app_info = app_info
        self._base_url = base_url
        self._timeout = timeout
        self._max_retries = max_retries
        self._logging = logging

    def get_headers(self, *, include_token: bool = True) -> typing.Dict[str, str]:
        import platform
        from importlib import metadata as _importlib_metadata

        try:
            _sdk_version = _importlib_metadata.version("getclean")
        except _importlib_metadata.PackageNotFoundError:
            _sdk_version = "0.1.0"

        _user_agent = "getclean/" + _sdk_version
        _os = platform.system().lower()
        _arch = platform.machine()
        if _arch.lower() in ("x64", "amd64", "x86_64"):
            _arch = "x86_64"
        _platform = "; ".join(part for part in (_os, _arch) if part)
        if _platform:
            _user_agent += f" ({_platform})"
        _python_version = platform.python_version()
        if _python_version:
            _user_agent += f" Python/{_python_version}"
        _user_agent = _append_app_info_to_user_agent(_user_agent, self._app_info)
        headers: typing.Dict[str, str] = {
            "User-Agent": _user_agent,
            **(self.get_custom_headers() or {}),
        }
        if include_token:
            api_key = self._get_api_key()
            if api_key is not None:
                headers["Authorization"] = f"Bearer {api_key}"
        return headers

    def _get_api_key(self) -> typing.Optional[str]:
        if isinstance(self._api_key, str) or self._api_key is None:
            return self._api_key
        else:
            return self._api_key()

    def get_custom_headers(self) -> typing.Optional[typing.Dict[str, str]]:
        return self._headers

    def get_base_url(self) -> str:
        return self._base_url

    def get_timeout(self) -> typing.Optional[float]:
        return self._timeout

    def get_max_retries(self) -> int:
        return self._max_retries


class SyncClientWrapper(BaseClientWrapper):
    def __init__(
        self,
        *,
        api_key: typing.Optional[typing.Union[str, typing.Callable[[], str]]] = None,
        headers: typing.Optional[typing.Dict[str, str]] = None,
        app_info: typing.Optional[typing.Dict[str, str]] = None,
        base_url: str,
        timeout: typing.Optional[float] = None,
        max_retries: int = 4,
        logging: typing.Optional[typing.Union[LogConfig, Logger]] = None,
        httpx_client: httpx.Client,
    ):
        super().__init__(
            api_key=api_key,
            headers=headers,
            app_info=app_info,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            logging=logging,
        )
        self.httpx_client = HttpClient(
            httpx_client=httpx_client,
            base_headers=self.get_headers,
            base_timeout=self.get_timeout,
            base_url=self.get_base_url,
            base_max_retries=self.get_max_retries(),
            logging_config=self._logging,
        )


class AsyncClientWrapper(BaseClientWrapper):
    def __init__(
        self,
        *,
        api_key: typing.Optional[typing.Union[str, typing.Callable[[], str]]] = None,
        headers: typing.Optional[typing.Dict[str, str]] = None,
        app_info: typing.Optional[typing.Dict[str, str]] = None,
        base_url: str,
        timeout: typing.Optional[float] = None,
        max_retries: int = 4,
        logging: typing.Optional[typing.Union[LogConfig, Logger]] = None,
        async_token: typing.Optional[typing.Callable[[], typing.Awaitable[str]]] = None,
        httpx_client: httpx.AsyncClient,
    ):
        super().__init__(
            api_key=api_key,
            headers=headers,
            app_info=app_info,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            logging=logging,
        )
        self._async_token = async_token
        self.httpx_client = AsyncHttpClient(
            httpx_client=httpx_client,
            base_headers=self.get_headers,
            base_timeout=self.get_timeout,
            base_url=self.get_base_url,
            base_max_retries=self.get_max_retries(),
            async_base_headers=self.async_get_headers,
            logging_config=self._logging,
        )

    async def async_get_headers(self) -> typing.Dict[str, str]:
        headers = self.get_headers(include_token=self._async_token is None)
        if self._async_token is not None:
            token = await self._async_token()
            headers["Authorization"] = f"Bearer {token}"
        return headers
