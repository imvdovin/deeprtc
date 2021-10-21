from pathlib import Path
from dataclasses import dataclass


@dataclass(frozen=True)
class SaveFileResult:
    path: Path
    name: str
