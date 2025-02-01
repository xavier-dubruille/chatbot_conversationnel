from starlette.responses import Response

import apps
from utils import get_user

app = apps.fast_app


@app.route("/api/ping")
def get():
    return "{status:ok}"


@app.route("/api/user")
def get(request):
    user, user_type, is_student = get_user(request)
    return f" Utilisateur connecté : {user} <br> Student Type : {user_type} <br> Is Student : {is_student}"


@app.route("/api/logout")
async def logout(request):
    return Response("Logout. Retournez sur la page principale pour vous reconnecter.", status_code=401)
