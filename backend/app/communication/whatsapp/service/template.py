"""
"""

from dataclasses import dataclass

from app.communication.whatsapp.template import (
    WhatsAppTemplateLanguage,
    WhatsAppTemplateCategory,
    WhatsAppTemplateApprovalStatus,
    WhatsAppTemplateStatus,
    WhatsAppTemplate
)
from app.communication.whatsapp.client import WhatsAppClient
from app.communication.whatsapp.exceptions import *


@dataclass(frozen = True)
class WhatsAppTemplateCreateResult:
    id: str
    approval_status: WhatsAppTemplateApprovalStatus

@dataclass(frozen = True)
class WhatsAppTemplateGetResult:
    name: str
    meta_id: str | None
    language: WhatsAppTemplateLanguage
    category: WhatsAppTemplateCategory
    body: str
    header: str | None
    footer: str | None
    approval_status: WhatsAppTemplateApprovalStatus
    status: WhatsAppTemplateStatus | None

@dataclass(frozen = True)
class WhatsAppTemplateRefreshStatusResult:
    name: str
    meta_id: str
    language: WhatsAppTemplateLanguage
    status: WhatsAppTemplateStatus | None

@dataclass(frozen = True)
class WhatsAppTemplateRefreshApprovalStatusResult:
    name: str
    meta_id: str
    language: WhatsAppTemplateLanguage
    approval_status: WhatsAppTemplateApprovalStatus

class WhatsAppTemplateService:
    def __init__(self, client: WhatsAppClient):
        self._client = client

    @property
    def client(self) -> WhatsAppClient:
        return self._client

    def _create_get_result(self, data) -> WhatsAppTemplateGetResult:
        try:
            name = data["name"]
            meta_id = data["id"]
            language = WhatsAppTemplateLanguage(data["language"])
            category = WhatsAppTemplateCategory(data["category"])

            body = None
            header = None
            footer = None
            
            for content in data["components"]:
                match content["type"]:
                    case "HEADER":
                        header = content["text"]

                    case "BODY":
                        body = content["text"]

                    case "FOOTER":
                        footer = content["text"]

                    case _:
                        pass

            if not body:
                raise

            status = None
            approval_status = None

            try:
                status = WhatsAppTemplateStatus(data["status"])
                approval_status = WhatsAppTemplateApprovalStatus.APPROVED

            except Exception:
                # so status is rejected or pending
                approval_status = WhatsAppTemplateApprovalStatus(data["status"])

            if not approval_status:
                raise

            return WhatsAppTemplateGetResult(
                name = name, 
                meta_id = meta_id,
                language = language,
                category = category,
                body = body,
                header = header,
                footer = footer,
                approval_status = approval_status,
                status =  status                     
            )

        except Exception as exc:
            raise WhatsAppInvalidInputsError(
                    f"""
                        WhatsApp Template Get: invalid data given for template get result generation: {str(exc)}.
                    """
            ) from exc

    def _create_refresh_status_result(self, data) -> WhatsAppTemplateRefreshStatusResult:
        try:
            name = data["name"]
            meta_id = data["id"]
            language = WhatsAppTemplateLanguage(data["language"])
            status = None

            try:
                status = WhatsAppTemplateStatus(data["status"])

            except Exception as exc:
                # This means status is some value of approval status
                pass

            return WhatsAppTemplateRefreshStatusResult(
                name = name,
                meta_id = meta_id,
                language = language,
                status = status
            )

        except Exception as exc:
            raise WhatsAppInvalidInputsError(
                    f"""
                        WhatsApp Template Refresh Result: invalid data given for template status result generation: {str(exc)}.
                    """
            ) from exc

    def _create_refresh_approval_status_result(self, data) -> WhatsAppTemplateRefreshApprovalStatusResult:
        try:
            name = data["name"]
            meta_id = data["id"]
            language = WhatsAppTemplateLanguage(data["language"])
            approval_status = WhatsAppTemplateApprovalStatus.APPROVED

            try:
                approval_status = WhatsAppTemplateApprovalStatus(data["status"])

            except Exception as exc:
                # This means that status is some value of status class, so it must be approved
                pass

            return WhatsAppTemplateRefreshApprovalStatusResult(
                name = name,
                meta_id = meta_id,
                language = language,
                approval_status = approval_status
            )

        except Exception as exc:
            raise WhatsAppInvalidInputsError(
                f"""
                    WhatsApp Template Refresh Result: invalid data given for template approval status result generation: {str(exc)}.
                """
            ) from exc

    def create(self, template: WhatsAppTemplate) -> WhatsAppTemplateCreateResult:
        template.validate()

        payload = {
            "name": template.name,
            "language": template.language.value,
            "category": template.category.value,
            "components": []
        }

        if template.header:
            payload["components"].append(
                {
                    "type": "HEADER",
                    "format": "TEXT",
                    "text": template.header
                }
            )

        payload["components"].append(
            {
                "type": "BODY",
                "text": template.body
            }
        )

        if template.footer:
            payload["components"].append(
                {
                    "type": "FOOTER",
                    "text": template.footer
                }
            )

        # Raises 
        response = self._client.post(
            endpoint = self._client.api_template_endpoint,
            body = payload
        )

        json_value = response.json()

        return WhatsAppTemplateCreateResult(
            id = json_value["id"],
            approval_status = WhatsAppTemplateApprovalStatus(json_value["status"])
        )
        
    def delete(
            self,
            template_name: str,
            template_language: WhatsAppTemplateLanguage | None
    ) -> bool:
        if not template_name:
            # Not allowing to delete all templates atleast right now
            raise WhatsAppInvalidInputsError("WhatsApp Template Deletion: accidental(?) deletion of all templates requested.")

        params = {}
        params["name"] = template_name

        if template_language:
            params["language"] = template_language.value

        response = self._client.delete(
                endpoint = self._client.api_template_endpoint,
                params = params
        )
    
        return response.json()["success"]

    def get(
            self,
            template_name: str
    ) -> list[WhatsAppTemplateGetResult]:
        if not template_name:
            raise WhatsAppInvalidInputsError("WhatsApp Template Fetching: empty template name given.")

        params = {
            "name": template_name
        }

        response = self._client.get(
            endpoint = self._client.api_template_endpoint,
            params = params
        )

        json_value = response.json()

        template_data = json_value["data"]

        return [
            self._create_get_result(data) for data in template_data
        ]

    def get_by_id(
            self,
            template_whatsapp_id: str
    ) -> WhatsAppTemplateGetResult | None:
        pass

    def getall(self) -> list[WhatsAppTemplateGetResult]:
        response = self._client.get(
            endpoint = self._client.api_template_endpoint
        )

        json_value = response.json()

        template_data = json_value["data"]

        return [
            self._create_get_result(data) for data in template_data
        ]

    def refresh_status(
        self,
        template_name: str
    ) -> list[WhatsAppTemplateRefreshStatusResult]:
        params = {
            "name": template_name,
            "fields": "name,status,language"
        }

        response = self._client.get(
            endpoint = self._client.api_template_endpoint,
            params = params
        )

        json_value = response.json()

        template_data = json_value["data"]

        return [
            self._create_refresh_status_result(data) for data in template_data
        ]

    def refresh_approval_status(
        self,
        template_name: str
    ) -> list[WhatsAppTemplateRefreshApprovalStatusResult]:
        params = {
            "name": template_name,
            "fields": "name,status,language"
        }

        response = self._client.get(
            endpoint = self._client.api_template_endpoint,
            params = params
        )

        json_value = response.json()

        template_data = json_value["data"]

        return [
            self._create_refresh_approval_status_result(data) for data in template_data
        ]

    def refresh_status_all(self) -> list[WhatsAppTemplateRefreshStatusResult]:
        params = {
            "fields": "name,status,language"
        }

        response = self._client.get(
            endpoint = self._client.api_template_endpoint,
            params = params
        )

        json_value = response.json()

        template_data = json_value["data"]

        return [
            self._create_refresh_status_result(data) for data in template_data
        ]

    def refresh_approval_status_all(self) -> list[WhatsAppTemplateRefreshApprovalStatusResult]:
        params = {
            "fields": "name,status,language"
        }

        response = self._client.get(
            endpoint = self._client.api_template_endpoint,
            params = params
        )

        json_value = response.json()

        template_data = json_value["data"]

        return [
            self._create_refresh_approval_status_result(data) for data in template_data
        ]

