from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class DataClasMeta(type):
    def __new__(cls, name: str, bases: tuple, dct: dict[str, Any]) -> type:
        new_class = super().__new__(cls, name, bases, dct)
        return dataclass(frozen=True)(new_class)


class BaseDataClass(metaclass=DataClasMeta):
    def to_dict(self) -> dict[str, str | dict[str, Any]]:
        return self.__dict__.copy()
