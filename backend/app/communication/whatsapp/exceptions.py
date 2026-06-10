"""
"""


class WhatsAppInvalidInputsError(Exception):
    _MESSAGE = "Invalid input given: {msg}."

    def __init__(self, msg: str):
        super().__init__(self._MESSAGE.format(msg = msg))

