"""
"""

from sqlite3 import Error as sql3_error


class DatabaseCursorError(Exception):
    _MESSAGE = "Could not fetch database cursor."

    def __init__(self) -> None:
        super().__init__(self._MESSAGE)

    def message(self) -> str:
        return self._MESSAGE

class DatabaseExecutionError(Exception):
    _MESSAGE = "Error in database: {exc}"

    def __init__(self, sql_error: sql3_error) -> None:
        self._msg = self._MESSAGE.format(exc=sql_error)
        super().__init__(self._msg)

    def message(self) -> str:
        return self._msg

class DatabaseDuplicateEntryError(Exception):
    _MESSAGE = "Duplicate entry given."

    def __init__(self) -> None:
        super().__init__(self._MESSAGE)

    def message(self) -> str:
        return self._MESSAGE

class DatabaseAbsentEntryError(Exception):
    _MESSAGE = "Entry is absent."

    def __init__(self) -> None:
        super().__init__(self._MESSAGE)

    def message(self) -> str:
        return self._MESSAGE

