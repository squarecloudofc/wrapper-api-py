from __future__ import annotations

from datetime import datetime

from .base import BaseDataClass


class DeployData(BaseDataClass):
    id: str
    state: str
    date: datetime
