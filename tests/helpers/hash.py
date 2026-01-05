import hashlib
from pathlib import Path


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bytes_hash(bytes: bytes) -> str:
    return hashlib.sha256(bytes).hexdigest()
