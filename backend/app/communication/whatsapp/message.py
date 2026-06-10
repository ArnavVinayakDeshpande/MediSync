"""
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum, auto

from app.communication.whatsapp.exceptions import *
from app.communication.whatsapp.template.language import WhatsAppTemplateLanguage


class WhatsAppMessageType(StrEnum):
    TEXT = auto()
    TEMPLATE = auto()

class WhatsAppMessageStatus(StrEnum):
    PENDING = auto()
    SENT = auto()
    DELIVERED = auto()
    READ = auto()

@dataclass
class WhatsAppMessage:
    id: str
    whatsapp_id: str | None
    msg_type: WhatsAppMessageType
    recipient_number: str
    template_name: str | None
    template_id: str | None
    text: str | None
    language: WhatsAppTemplateLanguage | None

    sent_on: datetime | None
    delivered_on: datetime | None
    read_on: datetime | None
    created_on: datetime = field(default_factory = datetime.now)

    parameters: list[str] = field(default_factory = list)

    @property
    def is_sent(self) -> bool:
        return self.sent_on is not None

    @property
    def is_delivered(self) -> bool:
        return self.delivered_on is not None

    @property
    def is_ready(self) -> bool:
        return self.read_on is not None

    @property
    def status(self) -> WhatsAppMessageStatus:
        if self.read_on is not None:
            return WhatsAppMessageStatus.READ

        if self.delivered_on is not None:
            return WhatsAppMessageStatus.DELIVERED

        if self.sent_on is not None:
            return WhatsAppMessageStatus.SENT

        return WhatsAppMessageStatus.PENDING

    def validate(self):
        if not self.id:
            raise WhatsAppInvalidInputsError("WhatsApp Message: id")

        if self.msg_type == WhatsAppMessageType.TEXT:
            if not self.text:
                raise WhatsAppInvalidInputsError("WhatsApp Message: no text given in free-form message.")

            if self.template_name or self.template_id:
                raise WhatsAppInvalidInputsError("WhatsApp Message: template name/id given in a free-form message.")

            if self.parameters:
                raise WhatsAppInvalidInputsError("WhatsApp Message: parameters given in free-form message.")

            if self.language is not None:
                raise WhatsAppInvalidInputsError("WhatsApp Message: language parameter in free-form message.")

        elif self.msg_type == WhatsAppMessageType.TEMPLATE:
            if not self.template_name:
                raise WhatsAppInvalidInputsError("WhatsApp Message: no template name given in templated message.")
            elif not self.template_id:
                raise WhatsAppInvalidInputsError("WhatsApp Message: no template id given in templated message.")

            if not self.language:
                raise WhatsappInvalidInputsError("WhatsApp Mesage: no language given in templated message.")

            if self.text:
                raise WhatsAppInvalidInputsError("WhatsApp Message: text given in templated message.")

        if len(self.recipient_number) != 10:
            raise WhatsAppInvalidInputsError("WhatsApp Message: invalid length for recipient number given.")

        try:
            _ = int(self.recipient_number)

        except ValueError:
            raise WhatsAppInvalidInputsError("WhatsApp Message: recipient number contains non-numeric digits.")

    def __post_init__(self):
        self.validate()

