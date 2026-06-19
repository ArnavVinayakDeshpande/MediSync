"""

"""

from datetime import datetime, date
from pymongo.collection import Collection
from pymongo.errors import (
    PyMongoError,
    DuplicateKeyError
)

from app.database.exceptions import *
from app.communication.whatsapp.message import (
    WhatsAppMessageType,
    WhatsAppMessageStatus,
    WhatsAppMessage
)
from app.communication.whatsapp.template import (
    WhatsAppTemplateLanguage,
    WhatsAppTemplateCategory
)
from app.common.converter import (
    datetime_to_db_fmt,
    datetime_from_db_fmt,
    date_to_datetime_range,
    whatsapp_message_to_db_fmt,
    whatsapp_message_from_db_fmt
)


class WhatsAppMessageHistoryRepository:
    def __init__(self, collection: Collection) -> None:
        self._collection = collection

        # Create the indices
        self._collection.create_index(
            "id",
            unique = True
        )

        self._collection.create_index(
            "whatsapp_id",
            unique = True
        )

    @property
    def collection(self) -> Collection:
        return self._collection

    def insert(
        self,
        message: WhatsAppMessage
    ) -> None:
        try:
            self._collection.insert_one(
                document = whatsapp_message_to_db_fmt(message)
            )
            
        except DuplicateKeyError as exc:
            raise DatabaseDuplicateEntryError() from exc

        except PyMongoError as exc:
            raise DatabaseExecutionError(exc) from exc

    def delete(self, message_id: str) -> None:
        try:
            result = self._collection.delete_one(
                filter = {
                    "id": message_id
                }
            )

            if result.deleted_count == 0:
                raise DatabaseAbsentEntryError()
        
        except PyMongoError as exc:
            raise DatabaseExecutionError(exc) from exc

    def get(self, message_id: str) -> WhatsAppMessage | None:
        try:
            message = self._collection.find_one(
                filter = {
                    "id": message_id
                }
            )

            return whatsapp_message_from_db_fmt(message) if message else None

        except PyMongoError as exc:
            raise DatabaseExecutionError(exc) from exc
            
    def getall(
        self,
        size: int = 0,
        offset: int = 0,
        msg_type: WhatsAppMessageType | None = None,
        recipient_number: str | None = None,
        template_name: str | None = None,
        template_id: str | None = None,
        language: WhatsAppTemplateLanguage | None = None,
        sent_on: date | None = None,
        created_on: date | None = None
    ) -> list[WhatsAppMessage]:
        so_start = None
        so_end = None
        co_start = None
        co_end = None

        if sent_on is not None:
           sent_on_start, sent_on_end = date_to_datetime_range(sent_on) 
           so_start = datetime_to_db_fmt(sent_on_start)
           so_end = datetime_to_db_fmt(sent_on_end)

        if created_on is not None:
            created_on_start, created_on_end = date_to_datetime_range(created_on)
            co_start = datetime_to_db_fmt(created_on_start)
            co_end = datetime_to_db_fmt(created_on_end)

        try:
            result = (
                self._collection
                .find(
                    {
                        **({"msg_type": msg_type.value} if msg_type is not None else {}),
                        **({"recipient_number": recipient_number} if recipient_number else {}),
                        **({"template.name": template_name} if template_name else {}),
                        **({"template.id": template_id} if template_id else {}),
                        **({"language": language.value} if language is not None else {}),
                        **({"sent_on": {"$gte": so_start, "$lt": so_end}} if sent_on is not None else {}),
                        **({"created_on": {"$gte": co_start, "$lt": co_end}} if created_on is not None else {})
                    }
                )
                .sort(
                    [
                        ("created_on", -1),
                        ("id", 1)
                    ]
                )
                .skip(offset)
                .limit(size)
            )

            return [
                whatsapp_message_from_db_fmt(res) for res in result
            ]

        except PyMongoError as exc:
            raise DatabaseExecutionError(exc) from exc

