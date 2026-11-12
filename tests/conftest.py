"""Skips the tests marked `aiohttp` when the optional aiohttp extra is not installed; nothing else."""

import pytest


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    try:
        import httpx_aiohttp  # noqa: F401
    except ImportError:
        skip = pytest.mark.skip(reason="the aiohttp extra is not installed")
        for item in items:
            if "aiohttp" in item.keywords:
                item.add_marker(skip)
