from __future__ import annotations

from .base import BaseDataClass
from .language import Language


class UploadData(BaseDataClass):
    """
    Upload data class

    :ivar id: ID of the uploaded application
    :ivar name: Tag of the uploaded application
    :ivar language: Programming language of the uploaded application
    :ivar ram: Ram allocated for the uploaded application
    :ivar cpu: Cpu of the uploaded application
    :ivar description: Description of the uploaded application
    :ivar domain: Subdomain of the uploaded application (only in websites)
    :ivar cluster: Cluster where the application is hosted

    :type id: str
    :type name: str
    :type language: Language
    :type ram: confloat(ge=0)
    :type cpu: confloat(ge=0)
    :type domain: str | None = None
    :type description: str | None = None
    :type cluster: str
    """

    id: str
    name: str
    language: Language
    ram: float
    cpu: float
    cluster: str
    domain: str | None = None
    description: str | None = None
