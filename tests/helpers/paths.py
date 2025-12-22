from pathlib import Path
from dataclasses import dataclass


@dataclass(frozen=True)
class Paths:
    template: Path
    out: Path
