"""
"""

from requests.exceptions import RequestException, HTTPError


class WhatsAppInvalidInputsError(Exception):
    _MESSAGE = "Invalid input given: {msg}."

    def __init__(self, msg: str):
        super().__init__(self._MESSAGE.format(msg = msg))

class WhatsAppAPIError(Exception):
    def __init__(self, exc: RequestException):
        self.message = f"Ran into error while sending a request: {exc}"
        self.status_code: int | None = None
        self.body: str | None = None

        if isinstance(exc, HTTPError):
            self.message += f" status code: {exc.response.status_code}, \n body = {exc.response.text}"
            self.status_code = exc.response.status_code
            self.body = exc.response.text

        super().__init__(self.message)

