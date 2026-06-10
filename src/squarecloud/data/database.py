from .base_database import BaseDatabaseData
from .certificate import Certificate


class Database(BaseDatabaseData):
    memory: int
    cpu: int
    password: str
    certificate: Certificate
    connection_url: str
