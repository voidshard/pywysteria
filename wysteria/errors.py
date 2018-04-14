
class RequestTimeoutError(Exception):
    """The request took too long to come back -> something is down?"""
    pass


class UnknownMiddlewareError(Exception):
    """The config asks to use a middleware for which we can't find a class definition"""
    pass


class NoServersError(Exception):
    """No server(s) were found, or we were unable to establish a connection to them"""
    pass


class ConnectionClosedError(Exception):
    """The connection has been closed"""
    pass


class InvalidInputError(Exception):
    """The input data is malformed or otherwise invalid"""
    pass


class AlreadyExistsError(Exception):
    """Raised if an attempt was made to create something that already exists"""
    pass


class NotFoundError(Exception):
    """An given ID to some object was not found"""


class IllegalOperationError(Exception):
    """The requested operation is not permitted"""
    pass


class ServerUnavailableError(Exception):
    """The server is currently unavailable. (An admin has ordered it not to server requests)"""
    pass
