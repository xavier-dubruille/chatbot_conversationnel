# Note: j'ai regroupé ici les endpoints pour les keystrokes ainsi que les utils lié ainsi que la gestion de postgres,
# étant donné que je n'utilise pas postgres autre part (mais ca pourrait changer)
import json
import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import List

import psycopg_pool
from dotenv import load_dotenv
from starlette.exceptions import HTTPException

import apps
from utils import get_user

load_dotenv()
app = apps.fast_app

# Création du pool de connexions
postgres_user = os.getenv("postgres_user")
postgres_password = os.getenv("postgres_password")
postgres_database = os.getenv("postgres_database")
pool = psycopg_pool.ConnectionPool(
    f"postgresql://{postgres_user}:{postgres_password}@localhost:5432/{postgres_database}",
    min_size=1,
    max_size=10
)


@dataclass
class KeyStoke:
    key: str
    code: str
    timestamp: float


# Gestionnaire de contexte pour les connexions
@asynccontextmanager
async def get_db():
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)


async def _insert_keystroke_in_db(user: str, keystrokes: List[KeyStoke]):
    async with get_db() as conn:
        try:
            with conn.cursor() as cur:
                for keystroke in keystrokes:
                    query = """
                    INSERT INTO keystrokes (user, key, code, timestamp)
                    VALUES (%s, %s, %s, %s)
                    """
                    print("(debug) query: " + query)
                    cur.execute(query, (user, keystroke.key, keystroke.code, keystroke.timestamp))
                conn.commit()
        except Exception as e:
            conn.rollback()
            # idéalement, faudrait que j'envoie une autre exception après le rollback
            raise HTTPException(status_code=500, detail=str(e))


async def _create_keystroke_table():
    async with get_db() as conn:
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS keystokes (
                user TEXT NOT NULL,
                key TEXT NOT NULL,
                code TEXT NOT NULL,
                timestamp DOUBLE PRECISION NOT NULL
            );
            """)
            conn.commit()

        except Exception as e:
            conn.rollback()
            # idéalement, faudrait que je j'envoie une autre exception après le rollback
            raise HTTPException(status_code=500, detail=str(e))


def _parse_json_to_keyStokes(json_str) -> List[KeyStoke]:
    data = json.loads(json_str)
    return [KeyStoke(**item) for item in data]


@app.route("/api/keystrokes")
def post(body, request):
    user, _, _ = get_user(request)
    keystrokes = _parse_json_to_keyStokes(body)

    _insert_keystroke_in_db(user, keystrokes)

    # print("keystrokes: ", keystrokes)

    return "{status:ok}"


@app.route("/admin/create_keystroke_table")
def get(request):
    _, _, is_student = get_user(request)
    if is_student:
        return "{status:unauthorized}"

    _create_keystroke_table()

    return "{status:ok}"
