class Error(Exception):
    """Base class for LUMPSModel exceptions."""
    pass


class InvalidArgumentError(Error):
    """Exception raised for errors in the input.
    """
    pass


class ConfigValueNotRecognized(Error):
    pass