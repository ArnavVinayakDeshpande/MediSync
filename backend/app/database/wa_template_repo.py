"""

"""

from datetime import date, datetime
from dataclasses import dataclass
from pymongo.collection import Collection
from pymongo.errors import (
    PyMongoError,
    DuplicateKeyError   
)

from app.database.exceptions import *
from app.communication.whatsapp.template import (
    WhatsAppTemplateLanguage,
    WhatsAppTemplateCategory,
    WhatsAppTemplateApprovalStatus,
    WhatsAppTemplateStatus,
    WhatsAppTemplate
)
from app.common.converter import (
    datetime_to_db_fmt,
    datetime_from_db_fmt,
    date_to_datetime_range,
    whatsapp_template_to_db_fmt,
    whatsapp_template_from_db_fmt
)


@dataclass
class WhatsAppTemplateRepositoryGetFieldsResult:
    id: str 
    name: str | None
    meta_id: str | None
    language: WhatsAppTemplateLanguage | None
    category: WhatsAppTemplateCategory | None
    body: str | None
    header: str | None
    footer: str | None
    approval_status: WhatsAppTemplateApprovalStatus | None
    status: WhatsAppTemplateStatus | None
    created_on: datetime | None
    variables: list[str] | None

class WhatsAppTemplateRepository:
    def __init__(self, collection: Collection) -> None:
        self._collection = collection

        # Create the indices
        self._collection.create_index(
            "id",
            unique = True
        )

        self._collection.create_index(
            [
                "name", "language"
            ],
            unique = True
        )

        self._collection.create_index(
            "meta_id",
            unique = True
        )

    def insert(
        self,
        template: WhatsAppTemplate
    ) -> None:
        try:
            self._collection.insert_one(
                document = whatsapp_template_to_db_fmt(template)
            )

        except DuplicateKeyError as exc:
            raise DatabaseDuplicateEntryError() from exc

        except PyMongoError as exc:
            raise DatabaseExecutionError(exc) from exc

    def delete(self, template_id: str) -> None:
        try:
            result = self._collection.delete_one(
                filter = {
                    "id": template_id
                }
            )

            if result.deleted_count == 0:
                raise DatabaseAbsentEntryError()

        except PyMongoError as exc:
            raise DatabaseExecutionError(exc) from exc

    def delete_by_meta_id(self, meta_id: str) -> None:
        try:
            result = self._collection.delete_one(
                filter = {
                    "meta_id": meta_id
                }
            )

            if result.deleted_count == 0:
                raise DatabaseAbsentEntryError()

        except PyMongoError as exc:
            raise DatabaseExecutionError(exc) from exc

    def delete_by_name(
        self,
        name: str,
        language: WhatsAppTemplateLanguage | None = None
    ) -> None:
        try:
            result = self._collection.delete_one(
                filter = {
                    "name": name,
                    **({"language": language.value} if language is not None else {})
                }
            )

            if result.deleted_count == 0:
                raise DatabaseAbsentEntryError()

        except PyMongoError as exc:
            raise DatabaseExecutionError(exc) from exc

    def get(
        self,
        template_id: str
    ) -> WhatsAppTemplate | None:
        try:
            template = self._collection.find_one(
                {
                    "id": template_id
                }       
            )

            if template is None:
                return None

            return whatsapp_template_from_db_fmt(template)

        except PyMongoError as exc:
            raise DatabaseExecutionError(exc) from exc

    def get_by_meta_id(
        self,
        meta_id: str
    ) -> WhatsAppTemplate | None:
        try:
            template = self._collection.find_one(
                {
                    "meta_id": meta_id
                }
            )

            if template is None:
                return None

            return whatsapp_template_from_db_fmt(template)

        except PyMongoError as exc:
            raise DatabaseExecutionError(exc) from exc

    def get_by_name(
        self,
        name: str,
        language: WhatsAppTemplateLanguage | None = None
    ) -> WhatsAppTemplate | None:
        try:
            template= self._collection.find_one(
                {
                    "name": name,
                    **({"language": language.value} if language is not None else {})
                }
            )

            if template is None:
                return None

            return whatsapp_template_from_db_fmt(template)

        except PyMongoError as exc:
            raise DatabaseExecutionError(exc) from exc

    def getall(
        self,
        size: int = 0,
        offset: int = 0,
        name: str | None = None,
        language: WhatsAppTemplateLanguage | None = None,
        category: WhatsAppTemplateCategory | None = None,
        has_header: bool | None = None,
        has_footer: bool | None = None,
        approval_status: WhatsAppTemplateApprovalStatus | None = None,
        status: WhatsAppTemplateStatus | None = None, # TODO Figure out how to query for 'None' status.
        is_approved: bool | None = None,
        created_on: date | None = None,
        has_variables: bool | None = None
    ) -> list[WhatsAppTemplate]:
        co_start, co_end = None, None

        if created_on is not None:
            created_on_start, created_on_end = date_to_datetime_range(
                created_on
            )

            co_start = datetime_to_db_fmt(created_on_start)
            co_end = datetime_to_db_fmt(created_on_end)

        try:
            result = (
                self._collection.find(
                    {
                        **({"name": name} if name else {}),
                        **({"language": language.value} if language is not None else {}),
                        **({"category": category.value} if category is not None else {}),
                        **({"header": {"$ne": None} if has_header else None} if has_header is not None else {}),
                        **({"footer": {"$ne": None} if has_footer else None} if has_footer is not None else {}),
                        **({"approval_status": approval_status.value} if approval_status is not None else {}),
                        **({"status": status.value} if status is not None else {}),
                        **({"approval_status": WhatsAppTemplateApprovalStatus.APPROVED if is_approved else {"$ne": WhatsAppTemplateApprovalStatus.APPROVED}} if is_approved is not None else {}),
                        **({"created_on": {"$gte": co_start, "$lt": co_end}} if created_on is not None else {}),
                        **({"variables": {"$ne": []} if has_variables else []} if has_variables is not None else {})
                        
                    }
                )
                .sort(
                    [
                        ("name", 1),
                        ("language", 1),
                        ("id", 1)
                    ]
                )
                .skip(offset)
                .limit(size)
            )

            return [
                whatsapp_template_from_db_fmt(res)
                for res in result
            ]

        except PyMongoError as exc:
            raise DatabaseExecutionError(exc) from exc

    def getfields(
        self,
        template_id: str,
        name: bool = False,
        meta_id: bool = False,
        language: bool = False,
        category: bool = False,
        body: bool = False,
        header: bool = False,
        footer: bool = False,
        approval_status: bool = False,
        status: bool = False,
        created_on: bool = False,
        variables: bool = False
    ) -> WhatsAppTemplateRepositoryGetFieldsResult | None:
        try:
            result = self._collection.find_one(
                {
                    "id": template_id
                },
                {
                    "_id": 0,
                    "name": int(name),
                    "meta_id": int(meta_id),
                    "language": int(language),
                    "category": int(category),
                    "body": int(body),
                    "header": int(header),
                    "footer": int(footer),
                    "approval_status": int(approval_status),
                    "status": int(status),
                    "created_on": int(created_on),
                    "variables": int(variables)
                }
            )

            return WhatsAppTemplateRepositoryGetFieldsResult(
                id = template_id,
                name = result["name"] if name else None,
                meta_id = result["meta_id"] if meta_id else None,
                language = WhatsAppTemplateLanguage(result["language"]) if language else None,
                category = WhatsAppTemplateCategory(result["category"]) if category else None,
                body = result["body"] if body else None,
                header = result["header"] if header else None,
                footer = result["footer"] if footer else None,
                approval_status = WhatsAppTemplateApprovalStatus(result["approval_status"]) if approval_status else None,
                status = WhatsAppTemplateStatus(result["status"]) if status and result["status"] is not None else None,
                created_on = datetime_from_db_fmt(result["created_on"]) if created_on else None,
                variables = result["variables"] if variables else None
            ) if result else None

        except PyMongoError as exc:
            raise DatabaseExecutionError(exc) from exc

    def getid(self, meta_id: str) -> str | None:
        try:
            result = self._collection.find_one(
                {
                    "meta_id": meta_id
                },
                {
                    "_id": 0,
                    "id": 1
                }
            )

            return result["id"] if result is not None else None

        except PyMongoError as exc:
            raise DatabaseExecutionError(exc) from exc

    def update(self):
        pass

