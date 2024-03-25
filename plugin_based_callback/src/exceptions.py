# CR: Instead of all classes inheriting from Exception, we can create a custom exception class and inherit from it.
# CR: CallbackHandlerException, this will allow us to differentiate between our custom exceptions and other exceptions


class CallbackHandlerException(Exception):
    """Custom Callback Handler exception"""
    pass


class DatabaseConnectionError(CallbackHandlerException):
    """Exception raised when a database connection fails."""

    pass


class AuthenticationError(CallbackHandlerException):
    """Exception raised for errors in the authentication process."""

    pass


class PluginError(CallbackHandlerException):
    """Exception raised for errors within plugin operations."""

    pass


class ValidationError(CallbackHandlerException):
    """Exception raised for data validation errors."""

    pass


class DatabaseUnsupportedError(CallbackHandlerException):
    """Exception raised when an unsupported database type is specified."""

    pass


class PluginLoadError(CallbackHandlerException):
    """Exception raised when loading a plugin fails."""

    pass
