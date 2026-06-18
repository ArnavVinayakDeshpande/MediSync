"""
"""

from sqlite3 import Error as SqliteError
from pymongo.errors import PyMongoError


type InternalDatabaseError = SqliteError | PyMongoError

class DatabaseConfigurationError(Exception):
    _MESSAGE = "Invalid configuration given to database: {msg}"

    def __init__(self, message: str):
        super().__init__(self._MESSAGE.format(msg = message))

class DatabaseDisconnectedError(Exception):
    """Raised when a connection to the database cannot be established."""

    _MESSAGE = "Failed to establish a connection to the database."

    def __init__(self, exc: InternalDatabaseError | None = None):
        if exc is None:
            super().__init__(self._MESSAGE)
        else:
            super().__init__(f"{self._MESSAGE} {exc}")

class DatabaseCursorError(Exception):
    _MESSAGE = "Failed to create database cursor: {exc}"

    def __init__(self, exc: InternalDatabaseError):
        super().__init__(self._MESSAGE.format(exc=exc))

class DatabaseExecutionError(Exception):
    """Raised when execution of a database operation fails."""

    _MESSAGE = "Database operation failed: {exc}"

    def __init__(self, exc: InternalDatabaseError):
        super().__init__(self._MESSAGE.format(exc = exc))


class DatabaseDuplicateEntryError(Exception):
    """Raised when attempting to insert a duplicate entry."""

    _MESSAGE = "An entry with the same unique key already exists."

    def __init__(self):
        super().__init__(self._MESSAGE)


class DatabaseAbsentEntryError(Exception):
    """Raised when the requested entry does not exist."""

    _MESSAGE = "The requested entry does not exist in the database."

    def __init__(self):
        super().__init__(self._MESSAGE)


class DatabaseParsingError(Exception):
    """Raised when database data cannot be converted into an object."""

    _MESSAGE = "Failed to parse database data into the required object."

    def __init__(self, exc: Exception | None = None):
        if exc is None:
            super().__init__(self._MESSAGE)
        else:
            super().__init__(f"{self._MESSAGE} ({exc})")

