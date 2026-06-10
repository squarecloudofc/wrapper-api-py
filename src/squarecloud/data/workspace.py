from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseDataClass

if TYPE_CHECKING:
    from .. import Application


class Member(BaseDataClass):
    """
    Workspace member data class

    :ivar id: Member identifier
    :ivar name: Member display name
    :ivar group: Member group or role in the workspace

    :type id: str
    :type name: str
    :type group: str
    """

    id: str
    name: str
    group: str


class Workspace(BaseDataClass):
    """
    Workspace data class

    :ivar id: Workspace identifier
    :ivar name: Workspace name
    :ivar owner: Workspace owner member
    :ivar members: List of workspace members
    :ivar applications: List of applications in the workspace
    :ivar created_at: Workspace creation timestamp

    :type id: str
    :type name: str
    :type owner: Member
    :type members: list[Member]
    :type applications: list['Application']
    :type created_at: str
    """

    id: str
    name: str
    owner: Member
    members: list[Member]
    applications: list[Application]
    createdAt: str