# Part of the generated SDK of the getclean API; do not edit.


class ConfigurationError(Exception):
    """
    Raised when the client is built without a value it needs, such as a credential that is neither
    passed to the client nor set in the environment. No request has been sent; the message says what
    to pass or to set.
    """

    message: str

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
