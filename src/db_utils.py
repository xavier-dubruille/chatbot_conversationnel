import os
from contextlib import contextmanager
from http.client import HTTPException
from typing import List

import psycopg2
from dotenv import load_dotenv

from utils import KeyStoke

load_dotenv()

postgres_user = os.getenv("postgres_user")
postgres_password = os.getenv("postgres_password")
postgres_database = os.getenv("postgres_database")


@contextmanager
def get_db():
    # Crée une nouvelle connexion à chaque fois
    conn = psycopg2.connect(
        dbname=postgres_database,
        user=postgres_user,
        password=postgres_password,
        host="127.0.0.1",
        port=5432
    )
    try:
        yield conn
    finally:
        conn.close()


def insert_keystroke_in_db(user: str, keystrokes: List[KeyStoke]):
    with get_db() as conn:
        try:
            with conn.cursor() as cur:
                for keystroke in keystrokes:
                    query = """
                    INSERT INTO keystrokes (user_name, key, code, timestamp)
                    VALUES (%s, %s, %s, %s)
                    """
                    print("(debug) query: " + query)
                    cur.execute(query, (user, keystroke.key, keystroke.code, keystroke.timestamp))
                conn.commit()
        except Exception as e:
            conn.rollback()
            # faudrait que une autre exception !
            raise HTTPException(status_code=500, detail=str(e))


async def create_keystroke_table():
    async with get_db() as conn:
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS keystrokes (
                user_name TEXT NOT NULL,
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
