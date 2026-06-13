"""
"""

import sqlite3 as sql3
import datetime as datetime
import json

from app.database.exceptions import *
from app.communication.whatsapp.template import (
    WhatsAppTemplateLanaguage,
    WhatsAppTemplateCategory,
    WhatsAppTemplateApprovalStatus,
    WhatsAppTemplateStatus,
    WhatsAppTemplate
)
from app.common.converter import (
    date_to_db_fmt,
    date_from_db_fmt
)


class WhatsAppTemplateRepository:
    def __init__(self, connection: sql3.Connection):
        self.connection = connection

        self._ensure_initialized()

    def _get_cursor(self) -> sql3.Cursor:
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
                        wa_templates (
                            id TEXT PRIMARY KEY NOT NULL,
                            name TEXT NOT NULL,
                            meta_id TEXT UNIQUE,
                            language TEXT,
                            category TEXT NOT NULL,
                            body TEXT NOT NULL,
                            header TEXT,
                            footer TEXT,
                            approval_status TEXT NOT NULL,
                            status TEXT,
                            approved_on TEXT,
                            created_on TEXT NOT NULL,
                            variables TEXT NOT NULL
                        )
                """
            )

            self.commit()

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc

        finally:
            cursor.close()

    def _create_template(self, data) -> WhatsAppTemplate:
        try:
            return WhatsAppTemplate(
                id = data[0],
                name = data[1],
                meta_id = data[2],
                language = WhatsAppTemplateLanguage(data[3]),
                category = WhatsAppTemplateCategory(data[4]),
                body = data[5],
                header = data[6],
                footer = data[7],
                approval_status = WhatsAppTemplateApprovalStatus(data[8]),
                status = WhatsAppTemplateStatus(data[9]),
                approved_on = date_from_db_fmt(data[10]),
                created_on = date_from_db_fmt(data[11]),
                variables = json.loads(data[12])
            )

        except Exception as exc:
            raise DatabaseParsingError(exc) from exc

    def insert(
        self,
        template: WhatsAppTemplate
    ):
        template.validate()

        cursor = self._get_cursor()o
        
        try:
            cursor.execute(
                """
                    INSERT INTO 
                        wa_templates (
                            id,
                            name,
                            meta_id,
                            language,
                            category,
                            body,
                            header,
                            footer,
                            approval_status,
                            status,
                            approved_on,
                            created_on,
                            variables,
                        )
                    VALUES (
                        ?, ?, ?,
                        ?, ?, ?,
                        ?, ?, ?,
                        ?, ?, ?,
                        ?
                    )

                """,
                (
                    template.id,
                    template.name,
                    template.meta_id,
                    template.language.value,
                    template.category.value,
                    template.body,
                    template.header,
                    template.footer,
                    template.approval_status.value,
                    template.status.value,
                    date_to_db_fmt(template.approved_on),
                    date_to_db_fmt(template.created_on),
                    json.dumps(template.variables)
                )
            )

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc

        finally:
            cursor.close()

    def delete(
        self,
        template_id: str
    ):
        cursor = self._get_cursor()

        try:
            cursor.execute(
                """
                    DELETE FROM wa_templates
                    WHERE id = ?
                """,
                (template_id,)
            )

            if cursor.rowcount == 0:
                raise DatabaseAbsentEntryError()

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc

        finally:
            cursor.close()

    def delete_by_name(
        self,
        template_name: str,
        template_language: WhatsAppTemplateLanguage | None
    ):
        cursor = self._get_cursor()

        query = "DELETE FROM wa_templates WHERE name = ?"
        parameters = [template_name]

        if template_language is not None:
            query += " AND language = ? "
            parameters.append(template_language.value)

        try:
            cursor.exceute(
                query,
                parameters
            )

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc

        finally:
            cursor.close()

    def get(
        self, 
        template_id: str
    ) -> WhatsAppTemplate | None:
        cursor = self._get_cursor()
        
        try:
            cursor.exceute(
                """
                    SELECT * FROM wa_templates WHERE id = ?
                """,
                (template_id, )
            )

            data = cursor.fetchone()

            return self._create_template(data) if data is not None else None

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc

        finally:
            cursor.close()

    def getall(
        self,
        template_name: str | None,
        template_language: WhatsAppTemplateLanguage | None
    ) -> list[WhatsAppTemplate]:
        cursor = self._get_cursor() 

        query = "SELECT * FROM wa_templates"
        parameters = []

        if template_name:
            query += " WHERE name = ?"
            parameters.append(template_name)

            if template_language:
                query += " AND language = ?"
                parameters.append(template_language.value)

        else:
            if template_language:
                query += " WHERE language = ?"
                parameters.append(template_language.value)
        
        try:
            cursor.execute(
                query,
                parameters
            )

            data = cursor.fetchall()

            return [self._create_template(d) for d in data]

        except sql3.Error as exc:
            raise DatabaseExecutionError(exc) from exc

        finally:
            cursor.close()

    def update(
        self,
        template_id: str,
        set_header: bool = False,
        set_footer: bool = False,
        set_status: bool = False,
        set_approved_on: bool = False,
        set_approval_status: bool = False,
        header: str | None = None,
        footer: str | None = None,
        approval_status: WhatsAppTemplateApprovalStatus | None = None,
        status: WhatsAppTemplateStatus | None = None,
        approved_on: datetime | None = None
    ):
        cursor = self._get_cursor()

        if (
            not set_header and
            not set_footer and
            not set_status and
            not set_approved_on and
            not set_approval_status
        ):
            return  # No changes

        query = "UPDATE wa_templates SET"
        parameters = []

        try:
            first = True

            if set_header:
                if not first:
                    query += ","
                query += " header = ?"
                parameters.append(header)
                first = False

            if set_footer:
                if not first:
                    query += ","
                query += " footer = ?"
                parameters.append(footer)
                first = False

            if set_status:
                if not first:
                    query += ","
                query += " status = ?"
                parameters.append(status.value if status is not None else None)
                first = False

            if set_approval_status:
                if not first:
                    query += ","
                query += " approval_status = ?"
                parameters.append(
                    approval_status.value if approval_status is not None else None
                )
                first = False

            if set_approved_on:
                if not first:
                    query += ","
                query += " approved_on = ?"
                parameters.append(date_to_db_fmt(approved_on))
                first = False

            query += " WHERE id = ?"
            parameters.append(template_id)

            cursor.execute(query, parameters)

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

