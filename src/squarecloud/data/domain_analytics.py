from __future__ import annotations

from datetime import datetime

from .base import BaseDataClass


class DomainAnalytics(BaseDataClass):
    class BaseAnalytics(BaseDataClass):
        visits: int
        requests: int
        bytes: int
        date: str

        @property
        def date_time(self) -> datetime:
            "retrieves the date as a datetime object"
            return datetime.fromisoformat(self.date)

    class ExtraBaseAnalytics(BaseAnalytics):
        type: str

    class Visits(BaseAnalytics):
        pass

    class Countries(ExtraBaseAnalytics):
        pass

    class Devices(ExtraBaseAnalytics):
        pass

    class Os(ExtraBaseAnalytics):
        pass

    class Browsers(ExtraBaseAnalytics):
        pass

    class Protocols(ExtraBaseAnalytics):
        pass

    class Methods(ExtraBaseAnalytics):
        pass

    class Paths(ExtraBaseAnalytics):
        pass

    class Referers(ExtraBaseAnalytics):
        pass

    class Providers(ExtraBaseAnalytics):
        pass

    visits: list[Visits]
    countries: list[Countries]
    devices: list[Devices]
    os: list[Os]
    browsers: list[Browsers]
    protocols: list[Protocols]
    methods: list[Methods]
    paths: list[Paths]
    referers: list[Referers]
    providers: list[Providers]
