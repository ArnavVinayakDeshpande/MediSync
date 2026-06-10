"""
"""


class PMDatabaseError(Exception):
    """Raised when the patient manager encounters a database error."""

    _MESSAGE = "Patient manager database error: {exc}"

    def __init__(self, exc: Exception):
        super().__init__(self._MESSAGE.format(exc=exc))


class PMInvalidInputsError(Exception):
    """Raised when invalid patient inputs are provided."""

    _MESSAGE = "Invalid patient input: {msg}"

    def __init__(self, msg: str = "Validation failed."):
        super().__init__(self._MESSAGE.format(msg=msg))


class PMDuplicateEntryError(Exception):
    """Raised when a duplicate patient already exists."""

    _MESSAGE = "A patient with the given ID or phone number already exists."

    def __init__(self):
        super().__init__(self._MESSAGE)


class PMAbsentEntryError(Exception):
    """Raised when a patient does not exist."""

    _MESSAGE = "The requested patient does not exist."

    def __init__(self):
        super().__init__(self._MESSAGE)


class VMDatabaseError(Exception):
    """Raised when the visit manager encounters a database error."""

    _MESSAGE = "Visit manager database error: {exc}"

    def __init__(self, exc: Exception):
        super().__init__(self._MESSAGE.format(exc=exc))


class VMInvalidInputsError(Exception):
    """Raised when invalid visit inputs are provided."""

    _MESSAGE = "Invalid visit input: {msg}"

    def __init__(self, msg: str = "Validation failed."):
        super().__init__(self._MESSAGE.format(msg=msg))


class VMDuplicateEntryError(Exception):
    """Raised when a duplicate visit already exists."""

    _MESSAGE = "A visit with the given ID already exists."

    def __init__(self):
        super().__init__(self._MESSAGE)


class VMAbsentEntryError(Exception):
    """Raised when a visit does not exist."""

    _MESSAGE = "The requested visit does not exist."

    def __init__(self):
        super().__init__(self._MESSAGE)

