"""
"""

import sqlite3 as sql3
import json
from datetime import datetime

from app.database.exceptions import *
from app.communication.whatsapp.message import *
from app.communication.whatsapp.template import *
from app.common.converter import *


class WhatsAppMsgHistoryRepository:
    def __init__(self, connection: sql3.Connection):
        self.connection = connection

        self._ensure_initialized()

    def _get_cursor(self):
        try:
            return self.connection.cursor()

        except sql3.Error as exc:
            raise DatabaseCursorError(exc) from exc

    def _ensure_initialized(self):
        cursor = self._get_cursor()

        try:
            cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS
                        wa_message_history (
                            id TEXT PRIMARY KEY NOT NULL,
                            whatsapp_id TEXT UNIQUE,
                            msg_type TEXT NOT NULL,
                            recipient_number TEXT NOT NULL,
                            template_name TEXT,
                            template_id TEXT,
                            msg_text TEXT,
                            language TEXT,
                            sent_on TEXT,
                            delivered_on TEXT,
                            read_on TEXT,
                            created_on TEXT NOT NULL,
                            parameters TEXT NOT NULL
                            )
                    """
                    )

            self.commit()

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc

        finally:
            cursor.close()

    def _create_message(self, data: tuple) -> WhatsAppMessage:
        try:
            return WhatsAppMessage(
                    id = data[0],
                    whatsapp_id = data[1],
                    msg_type = WhatsAppMessageType(data[2]),
                    recipient_number = data[3],
                    template_name = data[4],
                    template_id = data[5],
                    text = data[6],
                    language = WhatsAppTemplateLanguage(data[7]) if data[7] is not None else None,
                    sent_on = date_from_db_fmt(data[8]),
                    delivered_on = date_from_db_fmt(data[9]),
                    read_on = date_from_db_fmt(data[10]),
                    created_on = date_from_db_fmt(data[11]),
                    parameters = json.loads(data[12])
                    )

        except Exception as exc:
            raise DatabaseParsingError() from exc

    def insert(
            self,
            message: WhatsAppMessage
        ):
        cursor = self._get_cursor() 

        try:
            cursor.execute(
                    """
                    INSERT INTO 
                        wa_message_history (
                            id,
                            whatsapp_id,
                            msg_type,
                            recipient_number,
                            template_name,
                            template_id,
                            msg_text,
                            language,
                            sent_on,
                            delivered_on,
                            read_on,
                            created_on,
                            parameters
                            )
                    VALUES
                        (
                            ?, ?, ?,
                            ?, ?, ?,
                            ?, ?, ?,
                            ?, ?, ?,
                            ?
                        )
                    """,
                    (
                        message.id,
                        message.whatsapp_id,
                        message.msg_type,
                        message.recipient_number,
                        message.template_name,
                        message.template_id,
                        message.text,
                        message.language if message.language else None,
                        date_to_db_fmt(message.sent_on),
                        date_to_db_fmt(message.delivered_on),
                        date_to_db_fmt(message.read_on),
                        date_to_db_fmt(message.created_on),
                        json.dumps(message.parameters)
                    )
                    )

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc

        finally:
            cursor.close()

    def delete(self, message_id: str):
        cursor = self._get_cursor()

        try:
            cursor.execute(
                    """
                    DELETE FROM wa_message_history WHERE id = ?
                    """,
                    (message_id,)
                )

            if cursor.rowcount == 0:
                raise DatabaseAbsentEntryError()

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc

        finally:
            cursor.close()

    def get(self, message_id: str) -> WhatsAppMessage | None:
        cursor = self._get_cursor()

        try:
            cursor.execute(
                    """
                    SELECT * FROM wa_message_history WHERE id = ?
                    """,
                    (message_id,)
                    )

            data = cursor.fetchone()

            if data is None:
                return None

            return self._create_message(data)

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc

        finally:
            cursor.close()

    def get_by_whatsapp_id(self, whatsapp_id: str) -> WhatsAppMessage | None:
        cursor = self._get_cursor()

        try:
            cursor.execute(
                    """
                    SELECT * FROM wa_message_history WHERE whatsapp_id = ?
                    """,
                    (whatsapp_id,)
                    )

            data = cursor.fetchone()

            if data is None:
                return None

            return self._create_message(data)

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc

        finally:
            cursor.close()

    def get_id_from_whatsapp_id(self, whatsapp_id: str) -> str | None:
        cursor = self._get_cursor()

        try:
            cursor.execute(
                    """
                    SELECT id FROM wa_message_history WHERE whatsapp_id = ?
                    """,
                    (whatsapp_id,)
                    )

            data = cursor.fetchone()

            return data[0] if data is not None else None

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc

        finally:
            cursor.close()

    def get_whatsapp_id_from_id(self, id: str) -> str | None:
        cursor = self._get_cursor()

        try:
            cursor.execute(
                    """
                    SELECT whatsapp_id FROM wa_message_history WHERE id = ?
                    """,
                    (id,)
                    )

            data = cursor.fetchone()

            return data[0] if data is not None else None
            
        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc

        finally:
            cursor.close()
        
    def getall(self) -> list[WhatsAppMessage]:
        cursor = self._get_cursor()

        try:
            cursor.execute(
                    """
                    SELECT * FROM wa_message_history
                    """
                    )

            data = cursor.fetchall()

            return [self._create_message(d) for d in data]

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc

        finally:
            cursor.close()

    def update(
            self, 
            message_id: str,
            set_sent_date: bool = False,
            set_delivered_date: bool = False,
            set_read_date: bool = False,
            sent_date: datetime | None = None,
            delivered_date: datetime | None = None,
            read_date: datetime | None = None
        ):
        if (
                not set_sent_date and
                not set_delivered_date and
                not set_read_date
            ):
            return

        cursor = self._get_cursor()

        query = "UPDATE wa_message_history SET"

        parameters = []

        try:
            if set_sent_date:
                query += " sent_on = ?"
                parameters.append(date_to_db_fmt(sent_date))

            if set_delivered_date:
                query += ", delivered_on = ?"
                parameters.append(date_to_db_fmt(delivered_date))

            if set_read_date:
                query += ", read_on = ?"
                parameters.append(date_to_db_fmt(read_date))

            query += " WHERE id = ?"
            parameters.append(message_id)

            cursor.execute(
                    query,
                    parameters
                    )

            if cursor.rowcount == 0:
                raise DatabaseAbsentEntryError()

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc
        
        finally:
            cursor.close()

    def commit(self):
        try:
            self.connection.commit()

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc

