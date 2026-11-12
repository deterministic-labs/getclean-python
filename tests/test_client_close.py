import asyncio

import httpx

from getclean import AsyncGetClean, GetClean


def test_the_client_closes_the_httpx_clients_it_created() -> None:
    client = GetClean(
        api_key="test-api-key",
    )
    httpx_clients = list(client._owned_httpx_clients)
    assert client._client_wrapper.httpx_client.httpx_client in httpx_clients
    with client as entered:
        assert entered is client
        assert not any(httpx_client.is_closed for httpx_client in httpx_clients)
    assert all(httpx_client.is_closed for httpx_client in httpx_clients)

    client = GetClean(
        api_key="test-api-key",
    )
    httpx_clients = list(client._owned_httpx_clients)
    assert client._client_wrapper.httpx_client.httpx_client in httpx_clients
    client.close()
    assert all(httpx_client.is_closed for httpx_client in httpx_clients)


def test_the_client_leaves_a_caller_supplied_httpx_client_open() -> None:
    supplied = httpx.Client()
    with GetClean(
        api_key="test-api-key",
        httpx_client=supplied,
    ) as client:
        assert client._client_wrapper.httpx_client.httpx_client is supplied
        assert client._owned_httpx_clients == []
    assert not supplied.is_closed
    supplied.close()


def test_the_async_client_closes_the_httpx_clients_it_created() -> None:
    async def main() -> None:
        client = AsyncGetClean(
            api_key="test-api-key",
        )
        httpx_clients = list(client._owned_httpx_clients)
        assert client._client_wrapper.httpx_client.httpx_client in httpx_clients
        async with client as entered:
            assert entered is client
            assert not any(httpx_client.is_closed for httpx_client in httpx_clients)
        assert all(httpx_client.is_closed for httpx_client in httpx_clients)

        client = AsyncGetClean(
            api_key="test-api-key",
        )
        httpx_clients = list(client._owned_httpx_clients)
        assert client._client_wrapper.httpx_client.httpx_client in httpx_clients
        await client.close()
        assert all(httpx_client.is_closed for httpx_client in httpx_clients)

    asyncio.run(main())


def test_the_async_client_leaves_a_caller_supplied_httpx_client_open() -> None:
    async def main() -> None:
        supplied = httpx.AsyncClient()
        async with AsyncGetClean(
            api_key="test-api-key",
            httpx_client=supplied,
        ) as client:
            assert client._client_wrapper.httpx_client.httpx_client is supplied
            assert client._owned_httpx_clients == []
        assert not supplied.is_closed
        await supplied.aclose()

    asyncio.run(main())
