"""
"""

from app.communication.whatsapp.client import WhatsAppClient
from app.communication.whatsapp.message import *
from app.communication.whatsapp.exceptions import *


class WhatsAppMessengerService:
    def __init__(
            self,
            client: WhatsAppClient 
        ):
        self._client = client

    @property
    def client(self) -> WhatsAppClient:
        return self._client

    def send(message: WhatsAppMessage) -> str:
        match message.msg_type:
            case WhatsAppMessageType.TEXT:
                return self.send_text(message)

            case WhatsAppMessageType.TEMPLATE:
                return self.send_template(message)

            case _:
                raise WhatsAppInvalidInputsError("WhatsApp Service: unknown message type.")

    def send_text(message: WhatsAppMessagee) -> str:
        payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": "91" + message.recipient_number,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": message.text
                    }
                } 

        response = self._client.post(
                endpoint = self._client.api_message_endpoint,
                body = payload
                )

        response.raise_for_status() # Wrap in an try: except latert

        body = response.json()

        return body["messages"][0]["id"]

    def send_template(message: WhatsAppMessage) -> str:
        payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": "91" + message.recipient_number,
                "type": "template",
                "template": {
                    "name": message.template_name,
                    "language": {
                        "code": message.language.value
                        }
                    },
                "components": [
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": parameter
                        } for parameter in message.parameters
                        ]
                    ]
                }

        response = self._client.post(
                endpoint = self._client.api_message_endpoint,
                body = payload
                )

        response.raise_for_status() # Wrap in an try: except latert

        body = response.json()

        return body["messages"][0]["id"]

