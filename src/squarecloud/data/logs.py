from .base import BaseDataClass


class LogsData(BaseDataClass):
    """Logs data class

    :ivar logs: A string containing logs of your application

    :type logs: str | str = ''
    """

    logs: str = ''

    def __eq__(self, other: object) -> bool:
        return isinstance(other, LogsData) and self.logs == other.logs
