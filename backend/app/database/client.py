"""
"""

import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import PyMongoError
from pymongo.database import Database
from urllib.parse import quote_plus

from app.database.exceptions import *


class MongoDBClient:
    def __init__(self):
        username = os.getenv("MONGODB_USERNAME")
        password = os.getenv("MONGODB_PASSWORD")

        if not username or not password:
            raise DatabaseConfigurationError(
                "No MONGODB_USERNAME or MONGODB_PASSWORD field present in environment variables to connect to MongoDB."
            )

        self._uri = (
            f"mongodb+srv://{username}:{quote_plus(password)}"
            "@lenestdevcluster.ws1ommw.mongodb.net/"
            "?appName=LenestDevCluster"
        )

        self._client = MongoClient(
            uri = self._uri,
            server_api = ServerApi("1")
        )

        # Try to ping
        try:
            self._client.admin.command("ping")

        except PyMongoError as exc:
            raise DatabaseDisconnectedError(exc) from exc

    @property
    def client(self) -> MongoClient:
        return self._client

    def get_database(self, name: str) -> Database:
        try:
            return self._client[name]

        except PyMongoError as exc:
            raise DatabaseExecutionError(exc) from exc

