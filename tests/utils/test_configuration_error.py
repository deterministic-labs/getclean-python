# Part of the generated SDK of the getclean API; do not edit.

import pytest

from getclean.core.api_error import ApiError
from getclean.core.configuration_error import ConfigurationError

MESSAGE = "api_key is required: pass it to the client or set the environment variable EXAMPLE_API_KEY."


def test_the_text_of_the_error_is_its_message_alone() -> None:
    error = ConfigurationError(MESSAGE)
    assert str(error) == MESSAGE
    assert error.message == MESSAGE


def test_a_configuration_error_is_not_an_error_of_an_http_response() -> None:
    assert not issubclass(ConfigurationError, ApiError)
    with pytest.raises(ConfigurationError) as raised:
        raise ConfigurationError(MESSAGE)
    assert not hasattr(raised.value, "status_code")
