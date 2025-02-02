from dataclasses import dataclass


@dataclass
class KeyStoke:
    key: str
    code: str
    timestamp: float
