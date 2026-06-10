from __future__ import annotations

from .base import BaseDataClass
from .plan import PlanData


class UserData(BaseDataClass):
    """
    User data class

    :ivar id: User ID;
    :ivar name: Username
    :ivar plan: User plan
    :ivar email: User email

    :type id: int
    :type name: str
    :type plan: PlanData
    :type email: str | None = None
    """

    id: int
    name: str
    plan: PlanData
    email: str | None = None
    locale: str | None = None
