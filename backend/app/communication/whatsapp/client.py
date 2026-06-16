"""
"""

import requests
from requests.exceptions import RequestException

from app.communication.whatsapp.exceptions import *


class WhatsAppClient:
    def __init__(
        self,
        access_token: str,
        phone_number_id: str,
        business_account_id: str,
        api_version: str = "v23.0"
    ):
        self._access_token = access_token
        self._phone_number_id = phone_number_id
        self._business_account_id = business_account_id
        self._api_version = api_version

    def _build_url(self, endpoint: str) -> str:
        return f"{self.api_base_url}/{endpoint}"

    @property
    def headers(self) -> dict[str, str]:
        return {
                "Authorization": f"Bearer {self._access_token}",
                "Content-Type": "application/json"
        }

    @property
    def api_base_url(self) -> str:
        return (
            f"""
                https://graph.facebook.com/{self._api_version}
            """
        )

    @property
    def phone_number_id(self) -> str:
        return self._phone_number_id

    @property
    def business_account_id(self) -> str:
        return self._business_account_id

    @property
    def api_version(self) -> str:
        return self._api_version

    @property
    def api_message_endpoint(self) -> str:
        return f"{self._business_account_id}/{self._phone_number_id}/messages"

    @property
    def api_template_endpoint(
        self,
        template_id: str | None
    ) -> str:
        return f"{template_id}" if template_id else f"{self._business_account_id}/message_templates"

    def _send(
        self,
        method,
        **kwargs
    ) -> requests.Response:
        try:
            response = method(timeout = 30, **kwargs)
            response.raise_for_status()
            return response

        except RequestException as exc:
            raise WhatsAppAPIError(exc) from exc

    def get(
        self,
        endpoint: str,
        params: dict | None = None
    ) -> requests.Response:
        return self._send(
                requests.get,
                url = self._build_url(endpoint),
                headers = self.headers,
                params = params
        )

    def post(
        self,
        endpoint: str,
        body: dict
    ) -> requests.Response:
        return self._send(
                requests.post,
                url = self._build_url(endpoint),
                headers = self.headers,
                json = body
        )

    def put(
        self,
        endpoint: str | None,
        body: dict
    ) -> requests.Response:
        return self._send(
                requests.put,
                url = self._build_url(endpoint),
                headers = self.headers,
                json = body
        )

    def delete(
        self,
        endpoint: str,
        params: dict | None = None
    ) -> requests.Response:
        return self._send(
                requests.delete,
                url = self._build_url(endpoint),
                headers = self.headers,
                params = params
        )

