from __future__ import annotations

from datetime import datetime

from .base import BaseDataClass


class AppData(BaseDataClass):
    """
    Application data class

    :ivar id: The application ID
    :ivar name: The application name
    :ivar cluster: The cluster that the app is hosted on
    :ivar ram: The amount of RAM that application is using
    :ivar language The programming language of the app.:
    :ivar domain: The domain of the application
    :ivar custom: The custom domain of the application
    :ivar desc: The description of the application
    :ivar created_at: The date when the application was created

    :type id: str
    :type name: str
    :type cluster: str
    :type ram: confloat(ge=0);
    :type lang: str | None
    :type domain: str | None = None
    :type custom: str | None = None
    :type desc: str | None = None
    """

    id: str
    name: str
    cluster: str
    ram: float
    cluster: str
    created_at: datetime
    lang: str | None
    domain: str | None = None
    custom: str | None = None
    desc: str | None = None
