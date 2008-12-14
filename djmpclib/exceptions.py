class ConfigError(Exception):
    """Raise an error if there are problems using data from djmpc_config.py"""
    pass

class ConnectionError(Exception):
    """Raised when djmpc has trouble connecting or disconnecting from the specified server."""
    pass

class InputError(Exception):
    """Raised when the user inputs some malformed or incorrect data."""
    pass
