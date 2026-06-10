from __future__ import annotations

from datetime import datetime

from .base import BaseDataClass


class SnapshotInfo(BaseDataClass):
    name: str
    size: int
    modified: datetime
    key: str

    @property
    def version_id(self) -> str:
        return self.key.split("versionId=")[-1]
