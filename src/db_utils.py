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
    if os.getenv("SKIP_DB_INSERT", False):
        print(f"{keystrokes}")
        print("Don't insert those keystrokes in database ...")
        return

    with get_db() as conn:
        try:
            with conn.cursor() as cur:
                query = """
                INSERT INTO keystrokes (user_name, key, code, timestamp)
                VALUES (%s, %s, %s, %s)
                """
                # Préparer les données à insérer en une seule fois
                data = [(user, keystroke.key, keystroke.code, keystroke.timestamp) for keystroke in keystrokes]

                # Exécution par lots
                cur.executemany(query, data)
                conn.commit()
        except Exception as e:
            conn.rollback()
            # faudrait une autre exception !
            raise HTTPException(e)


def create_keystroke_table():
    with get_db() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
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
            # faudrait une autre exception !
            raise HTTPException(e)


def create_chat_message_table():
    with get_db() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS chat_message (
                        id SERIAL PRIMARY KEY,
                        user_name TEXT NOT NULL,
                        assistant_msg TEXT,
                        user_msg TEXT,
                        start_assistant_timestamp DOUBLE PRECISION,
                        finished_assistant_timestamp DOUBLE PRECISION,
                        finished_user_timestamp DOUBLE PRECISION
                    );
                """)

            conn.commit()

        except Exception as e:
            conn.rollback()
            # faudrait une autre exception !
            raise HTTPException(e)


def save_chat_message_to_db(user_name: str, assistant_msg, user_msg,
                            assistant_started_timestamp,
                            assistant_finished_ts,
                            user_finished_ts):
    if os.getenv("SKIP_DB_INSERT", False):
        print(f'(DEBUG)  user:{user_name},  assitant_msg:{assistant_msg}, user_msg : {user_msg}, '
              f'assisstant_end_ts:{assistant_finished_ts},'
              f'user_finished_ts:{user_finished_ts}')
        print("Don't insert those messages in database ...")
        return
    with get_db() as conn:
        try:
            with conn.cursor() as cur:
                query = """
                INSERT INTO chat_message (user_name, assistant_msg, user_msg, start_assistant_timestamp, finished_assistant_timestamp, finished_user_timestamp) 
                VALUES (%s, %s, %s,%s, %s, %s)
                """
                # print("(debug) query: " + query)
                cur.execute(query, (
                    user_name, assistant_msg, user_msg, assistant_started_timestamp, assistant_finished_ts,
                    user_finished_ts))
            conn.commit()
        except Exception as e:
            conn.rollback()
            # faudrait une autre exception !
            raise HTTPException(e)
