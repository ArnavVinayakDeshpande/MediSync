"""
"""

import requests


class WhatsAppClient:
    def __init__(
            self,
            access_token: str,
            phone_number_id: str,
            business_account_id: str,
            api_version: str = "v23.0"):
        self._access_token = access_token
        self._phone_number_id = phone_number_id
        self._business_account_id = business_account_id
        self._api_version = api_version

    def _headers(self) -> dict[str, str]:
        return {
                "Authorization": f"Bearer {self._access_token}",
                "Content-Type": "application/json"
                }

    def _build_url(self, endpoint: str) -> str:
        return self.api_base_url + "/" + endpoint

    @property
    def api_base_url(self) -> str:
        return f"https://graph.facebook.com/{self._api_version}"

    @property
    def phone_number_id

    @property
    def api_message_endpoint(self) -> str:
        return f"{self._phone_number_id}/messages"

    @property
    def api_template_endpoint(self) -> str:
        return f"{self._business_account_id}/message_templates"

    def get(
            self,
            endpoint: str,
            params: dict | None = None) -> requests.Response:
        return requests.get(
                url = self._build_url(endpoint),
                headers = self._headers(),
                params = params,
                timeout = 30
                )

    def post(
            self,
            endpoint: str,
            body: dict) -> requests.Response:
        return requests.post(
                url = self._build_url(endpoint),
                headers = self._headers(),
                json = body,
                timeout = 30
                )

    def put(
            self,
            endpoint: str,
            body: dict) -> requests.Response:
        return requests.put(
                url = self._build_url(endpoint),
                headers = self._headers(),
                json = body,
                timeout = 30
                ) 

    def delete(
            self,
            endpoint: str,
            params: dict | None = None) -> requests.Response:
        return requests.delete(
                url = self._build_url(endpoint),
                headers = self._headers(),
                params = params,
                timeout = 30
                )

