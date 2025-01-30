import json
from dataclasses import dataclass
from typing import List

import apps

app = apps.fast_app


@dataclass
class KeyStoke:
    key: str
    code: str
    timestamp: float


def _parse_json_to_keyStokes(json_str) -> List[KeyStoke]:
    data = json.loads(json_str)
    return [KeyStoke(**item) for item in data]


@app.route("/api/ping")
def get():
    return "{status:ok}"


@app.route("/api/keystrokes")
def post(body):
    keystrokes = _parse_json_to_keyStokes(body)
    print("keystrokes: ", keystrokes)  # todo: save in db instead
    return "{status:ok}"
