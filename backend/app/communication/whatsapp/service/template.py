"""
"""

from app.communication.whatsapp.client import WhatsAppClient
from app.communication.whatsapp.exceptions import *
from app.communication.whatsapp.template import *


class WhatsAppTemplateService:
    def __init__(
            self,
            client: WhatsAppClient
        ):
        self._client = client

    @property
    def client(self) -> WhatsAppClient:
        return self._client

    def create(self, template: WhatsAppTemplate):
        payload = {}

        response = self._client.post(
                endpoint = self._client.api_message_template,
                body = payload
                )

    def update(self, template: WhatsAppTemplate):
        pass

    def delete_by_name(self, name: str):
        pass

    def delete_by_id(self, id: str):
        pass

    def delete_by_wa_id(self, wa_id: str):
        pass

    def get_by_name(self, name: str):
        pass

    def get_by_id(self, id: str):
        pass

    def get_by_wa_id(self, wa_id: str):
        pass

    def getall(self):
        pass

    def refresh_status_by_name(self, name: str):
        pass

    def refresh_status_by_id(self, id: str):
        pass

    def refresh_status_by_wa_id(self, wa_id: str):
        pass

    def refresh_approval_status_by_name(self, name: str):
        pass

    def refresh_approval_status_by_id(self, id: str):
        pass

    def refresh_approval_status_by_wa_id(self, wa_id: str):
        pass

    def refresh_status(self):
        pass

    def refresh_approval_status(self):
        pass

