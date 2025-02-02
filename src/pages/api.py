import json
from typing import List

from starlette.responses import Response

import apps
from connected_user import ConnectedUser
from db_utils import insert_keystroke_in_db, create_keystroke_table
from utils import KeyStoke

app = apps.fast_app


@app.route("/api/ping")
def get():
    return "{status:ok}"


@app.route("/api/user")
def get(request):
    user = ConnectedUser(request)
    return f" Utilisateur connecté : {user.user_name} <br> Student Type : {user.user_type} <br> Is Student : {user.is_student}"


@app.route("/api/logout")
async def logout(request):
    return Response("Logout. Retournez sur la page principale pour vous reconnecter.", status_code=401)


def _parse_json_to_keyStokes(json_str) -> List[KeyStoke]:
    data = json.loads(json_str)
    return [KeyStoke(**item) for item in data]


@app.route("/api/keystrokes")
async def post(body, request):
    user = ConnectedUser(request)
    keystrokes = _parse_json_to_keyStokes(body)

    insert_keystroke_in_db(user.user_name, keystrokes)

    print("keystrokes: ", keystrokes)

    return "{status:ok}"


@app.route("/admin/create_keystroke_table")
def get(request):
    user = ConnectedUser(request)
    if user.is_student:
        return "{status:unauthorized}"

    create_keystroke_table()

    return "{status:ok}"
