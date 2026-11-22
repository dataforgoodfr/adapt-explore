from dataclasses import dataclass
from typing import Any


@dataclass
class RawBatch:
    """Paquet de données brutes : créé par un driver, écrit par le stockage."""
    records: list[dict[str, Any]] | bytes   # bytes = fichier copié tel quel
    meta: dict                               # infos annexes (nom de fichier, url, API, date d'import, ect.) 