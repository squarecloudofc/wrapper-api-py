from __future__ import annotations

from typing import Any

from .base import BaseDataClass


class PlanData(BaseDataClass):
    """
    Plan data class

    :ivar name: The plan name
    :ivar memory: The plan memory available
    :ivar duration: Plan duration

    :type name: str
    :type memory: Dict[str, Any]
    :type duration: Dict[str, Any]
    """

    name: str
    memory: dict[str, Any]
    duration: int | None
