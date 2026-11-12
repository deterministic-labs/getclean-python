# Contributing

Thank you for taking the time to help.

## How this repository is built

Most of this SDK is generated from the getclean API's contract, one OpenAPI 3.1 file kept in the [getclean-api](https://github.com/deterministic-labs/getclean-api) repository. A change made to a generated file is lost at the next generation, so a problem in generated code is best reported as an issue here; it is fixed at its source and reaches the package at the next release.

The hand-written part is small: `src/getclean/client.py`, `src/getclean/_layer.py`, `src/getclean/errors/job_canceled.py`, `tests/conftest.py` and the tests under `tests/layer/`. One more file, `src/getclean/_problem_types.py`, is derived from the contract when the SDK is built and is never edited by hand. Changes to the hand-written files are welcome as pull requests.

## Reporting a problem

Open an issue with the version of `getclean`, your Python version, the call you made and what came back. Never paste your API key. For a security problem, see `SECURITY.md`.

## Running the checks

```sh
python -m venv .venv && source .venv/bin/activate
pip install -e ".[aiohttp]"
pip install mypy==1.13.0 ruff==0.11.5 pytest==9.1.1 pytest-asyncio==1.4.0 pytest-xdist==3.8.0 python-dateutil==2.9.0.post0 types-python-dateutil==2.9.0.20260807 urllib3==2.8.0
ruff check src tests
mypy src
pytest -q
```

## Pull requests

One change per pull request, with a test where the change has behavior. Run the three checks above before you open it. Write the commit subject in the imperative, capitalized, without a final period, and say in the body why the change is right when that is not plain from the diff.
