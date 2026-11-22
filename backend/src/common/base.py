from abc import ABC, abstractmethod
from typing import Iterator

from common.contracts import RawBatch


class BaseDriver(ABC):
    @abstractmethod
    def validate_config(self, config: dict) -> None:
        """erreur si la config de la source est incomplète."""

    @abstractmethod
    def fetch(self, config: dict, since: str | None = None) -> Iterator[RawBatch]:
        """Renvoie le brut par lots, sans le transformer."""

    @abstractmethod
    def healthcheck(self, config: dict) -> bool:
        """La source est joignable ? """