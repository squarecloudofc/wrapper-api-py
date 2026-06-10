from __future__ import annotations

from datetime import datetime

from .base_database import BaseDatabaseData


class DatabaseInfo(BaseDatabaseData):
    owner: str
    cluster: str
    port: int
    ram: int
    created_at: str

    @property
    def created_at_datetime(self) -> datetime:
        return datetime.fromisoformat(self.created_at)
