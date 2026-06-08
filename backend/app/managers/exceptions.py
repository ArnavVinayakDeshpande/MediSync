"""
"""


class PMDatabaseError(Exception):
    _MESSAGE = "Issue with database."

    def __init__(self) -> None:
        super().__init__(self._MESSAGE)

    def message(self) -> str:
        return self._MESSAGE

class PMInvalidInputsError(Exception):
    _MESSAGE = "Invalid inputs given to function."

    def __init__(self) -> None:
        super().__init__(self._MESSAGE)

    def message(self) -> str:
        return self._MESSAGE

class PMDuplicateEntryError(Exception):
    _MESSAGE = "Patient with same ID / number already exists."

    def __init__(self) -> None:
        super().__init__(self._MESSAGE)

    def message(self) -> str:
        return self._MESSAGE

class PMAbsentEntryError(Exception):
    _MESSAGE = "Patient with this ID does not exist."

    def __init__(self) -> None:
        super().__init__(self._MESSAGE)

    def message(self) -> str:
        return self._MESSAGE
    
