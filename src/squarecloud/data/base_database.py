from .base import BaseDataClass


class BaseDatabaseData(BaseDataClass):
    id: str
    name: str
    type: str
    cluster: str
