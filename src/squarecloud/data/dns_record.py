from .base import BaseDataClass


class DNSRecord(BaseDataClass):
    type: str
    name: str
    value: str
    status: str
