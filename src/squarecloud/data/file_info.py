from __future__ import annotations

from typing import Literal

from .base import BaseDataClass


class FileInfo(BaseDataClass):
    """
    File information

    :ivar type: return type of file
    :ivar name: File/Directory name
    :ivar size: File size
    :ivar lastModified: Last modification time
    :ivar path: File/Directory path

    :type type: Literal['file', 'directory']
    :type name: str
    :type size: int
    :type lastModified: int | float | None
    :type path: str
    """

    app_id: str
    type: Literal['file', 'directory']
    name: str
    path: str
    size: int = 0
    lastModified: int | float | None = None
