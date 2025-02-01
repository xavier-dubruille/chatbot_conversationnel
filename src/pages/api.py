import json
from dataclasses import dataclass
from typing import List

from starlette.responses import Response

import apps
from utils import user_type, is_student

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


@app.route("/api/user")
def get(request):
    user = request.headers.get("X-Remote-User", "Anonyme")
    return f" Utilisateur connecté : {user} <br> Student Type : {user_type(user)} <br> Is Student : {is_student(user)}"


@app.route("/api/logout")
async def logout(request):
    return Response("Logout. Retournez sur la page principale pour vous reconnecter.", status_code=401)


@app.route("/api/keystrokes")
def post(body):
    keystrokes = _parse_json_to_keyStokes(body)
    print("keystrokes: ", keystrokes)  # todo: save in db instead
    return "{status:ok}"
