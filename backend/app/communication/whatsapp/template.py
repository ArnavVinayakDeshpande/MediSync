"""
"""

from enum import StrEnum, auto
from dataclasses import dataclass, field
from datetime import datetime
import re

from app.communication.whatsapp.exceptions import *


class WhatsAppTemplateLanguage(StrEnum):
    ENGLISH = "en"
    ENGLISH_US = "en_US"
    ENGLISH_GB = "en_GB"

    HINDI = "hi"
    MARATHI = "mr"
    GUJARATI = "gu"
    BENGALI = "bn"
    PUNJABI = "pa"
    TAMIL = "ta"
    TELUGU = "te"
    KANNADA = "kn"
    MALAYALAM = "ml"

    FRENCH = "fr"
    GERMAN = "de"
    SPANISH = "es"

class WhatsAppTemplateCategory(StrEnum):
    MARKETING = "MARKETING"
    UTILITY = "UTILITY"
    AUTHENTICATION = "AUTHENTICATION"

class WhatsAppTemplateApprovalStatus(StrEnum):
    PENDING = auto()
    APPROVED = auto()
    REJECTED = auto()

class WhatsAppTemplateStatus(StrEnum):
    ACTIVE = auto()
    PAUSED = auto()
    DISABLED = auto()

@dataclass
class WhatsAppTemplate:
    id: str
    name: str
    meta_id: str | None
    language: WhatsAppTemplateLanguage
    category: WhatsAppTemplateCategory
    body: str
    header: str | None
    footer: str | None
    approval_status: WhatsAppTemplateApprovalStatus
    status: WhatsAppTemplateStatus | None
    approved_on: datetime | None
    created_on: datetime = field(default_factory = datetime.now)
    variables: list[str] = field(default_factory = list)

    def validate(self):
        if not self.id:
                raise WhatsAppInvalidInputsError(
                    "WhatsApp Template: no id given."
                )

        if not self.name:
            raise WhatsAppInvalidInputsError(
                "WhatsApp Template: no name given."
            )

        if not self.body:
            raise WhatsAppInvalidInputsError(
                "WhatsApp Template: no body given."
            )

        # Validate variables
        if len(set(self.variables)) != len(self.variables):
            raise WhatsAppInvalidInputsError(
                "WhatsApp Template: duplicate variable names."
            )

        for variable in self.variables:
            if not variable.strip():
                raise WhatsAppInvalidInputsError(
                    "WhatsApp Template: empty variable name."
                )

        # Extract placeholder numbers from the body
        matches = re.findall(r"\{\{(\d+)\}\}", self.body)
        placeholders = sorted(int(match) for match in matches)

        # Must be {{1}}, {{2}}, ..., {{n}}
        expected = list(range(1, len(placeholders) + 1))

        if placeholders != expected:
            raise WhatsAppInvalidInputsError(
                "WhatsApp Template: placeholders must be consecutively numbered from {{1}}."
            )

        # Number of placeholders must match number of variables
        if len(placeholders) != len(self.variables):
            raise WhatsAppInvalidInputsError(
                "WhatsApp Template: placeholder count does not match variable count."
            )

        if self.header is not None and not self.header.strip():
            raise WhatsAppInvalidInputsError(
                "WhatsApp Template: header cannot be empty."
            )

        if self.footer is not None and not self.footer.strip():
            raise WhatsAppInvalidInputsError(
                "WhatsApp Template: footer cannot be empty."
            )

        if (
            self.approval_status
            != WhatsAppTemplateApprovalStatus.APPROVED
            and self.status is not None
        ):
            raise WhatsAppInvalidInputsError(
                "WhatsApp Template: non-approved template cannot have a status."
            )

        if (
            self.approval_status
            == WhatsAppTemplateApprovalStatus.APPROVED
            and self.status is None
        ):
            raise WhatsAppInvalidInputsError(
                "WhatsApp Template: approved template must have a status."
            )

        if (
            self.approval_status
            == WhatsAppTemplateApprovalStatus.APPROVED
            and self.approved_on is None
        ):
            raise WhatsAppInvalidInputsError(
                "WhatsApp Template: approved template missing approval time."
            )

        if (
            self.approval_status
            != WhatsAppTemplateApprovalStatus.APPROVED
            and self.approved_on is not None
        ):
            raise WhatsAppInvalidInputsError(
                "WhatsApp Template: unapproved template has approval time."
            )

    def __post_init__(self):
        self.validate()
    
    @property
    def variable_count(self) -> int:
        return len(self.variables)

    @property
    def is_approved(self) -> bool:
        return self.approval_status == WhatsAppTemplateApprovalStatus.APPROVED

