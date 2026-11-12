# Generated from the getclean API contract; do not edit.

import typing

import httpx

SDK_DEFAULT_TIMEOUT: typing.Optional[float] = 120

try:
    import httpx_aiohttp  # type: ignore[import-not-found]
except ImportError:

    class DefaultAioHttpClient(httpx.AsyncClient):  # type: ignore
        def __init__(self, **kwargs: typing.Any) -> None:
            raise RuntimeError("To use the aiohttp client, install the aiohttp extra: pip install getclean[aiohttp]")

else:

    class DefaultAioHttpClient(httpx_aiohttp.HttpxAiohttpClient):  # type: ignore
        def __init__(self, **kwargs: typing.Any) -> None:
            kwargs.setdefault("timeout", SDK_DEFAULT_TIMEOUT)
            kwargs.setdefault("follow_redirects", True)
            super().__init__(**kwargs)


class DefaultAsyncHttpxClient(httpx.AsyncClient):
    def __init__(self, **kwargs: typing.Any) -> None:
        kwargs.setdefault("timeout", SDK_DEFAULT_TIMEOUT)
        kwargs.setdefault("follow_redirects", True)
        super().__init__(**kwargs)
