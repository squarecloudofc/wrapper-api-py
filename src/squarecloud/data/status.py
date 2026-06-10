from __future__ import annotations

from typing import Any

from .base import BaseDataClass


class StatusData(BaseDataClass):
    """
    Application status class

    :ivar cpu: the cpu used
    :ivar ram: the ram used
    :ivar status: the actual status of the application
    :ivar running: weather the application is running
    :ivar storage: storage used by the application
    :ivar network: network information
    :ivar uptime: uptime of the application
    :ivar time: time of the application

    :type cpu: str
    :type ram: str
    :type status: str
    :type running: bool
    :type storage: str
    :type network: Dict[str, Any]
    :type requests: conint(ge=0)
    :type uptime: int
    :type time: int | None = None
    """

    cpu: str
    ram: str
    status: str
    running: bool
    storage: str
    network: dict[str, Any]
    uptime: int | None = None
    time: int | None = None


class ResumedStatus(BaseDataClass):
    id: str
    running: bool
    cpu: str = "0.00%"
    ram: str = "0.00MB"
