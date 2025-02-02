from dataclasses import dataclass


@dataclass
class KeyStoke:
    key: str
    code: str
    timestamp: float


def get_user(request):
    user = request.headers.get("X-Remote-User", "Anonyme")
    user_type = _user_type(user)
    is_student = user_type != 'other'

    return user, user_type, is_student


def _user_type(login):
    if login.startswith("TI"):
        return 'ti'
    elif login.startswith("eB"):
        return 'eb'
    else:
        return 'other'
