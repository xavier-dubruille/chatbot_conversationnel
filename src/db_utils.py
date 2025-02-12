import os
from contextlib import contextmanager
from http.client import HTTPException
from typing import List
import pandas as pd
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
    skip = ("True" == os.getenv("SKIP_DB_INSERT"))
    if skip:
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


def save_chat_message_to_db(user_name: str,
                            scenario_id: int,
                            assistant_msg, user_msg,
                            assistant_started_timestamp,
                            assistant_finished_ts,
                            user_finished_ts):
    skip = ("True" == os.getenv("SKIP_DB_INSERT"))
    if skip:
        print(f'(DEBUG)  user:{user_name}, scenario_id: {scenario_id} '
              f'assitant_msg:{assistant_msg}, user_msg : {user_msg}, '
              f'assisstant_end_ts:{assistant_finished_ts},'
              f'user_finished_ts:{user_finished_ts}')
        print("Don't insert those messages in database ...")
        return
    with get_db() as conn:
        try:
            with conn.cursor() as cur:
                query = """
                INSERT INTO chat_message (user_name, scenario_id, assistant_msg, user_msg, start_assistant_timestamp, finished_assistant_timestamp, finished_user_timestamp) 
                VALUES (%s, %s, %s, %s,%s, %s, %s)
                RETURNING id
                """
                # print("(debug) query: " + query)
                cur.execute(query, (
                    user_name, scenario_id, assistant_msg, user_msg, assistant_started_timestamp, assistant_finished_ts,
                    user_finished_ts))
                inserted_id = cur.fetchone()[0]
            conn.commit()
        except Exception as e:
            conn.rollback()
            # faudrait une autre exception !
            raise HTTPException(e)
        return inserted_id


def save_feedback_to_db(feedback_msg: str, chat_id: int):
    skip = ("True" == os.getenv("SKIP_DB_INSERT"))
    if skip:
        print(f'(DEBUG)  chat_id: {chat_id} feedback: {feedback_msg}')
        print("Don't insert those messages in database ...")
        return
    with get_db() as conn:
        try:
            with conn.cursor() as cur:
                query = """
                INSERT INTO feedback_message (feedback_message, chat_message_id) 
                VALUES (%s, %s)
                """
                # print("(debug) query: " + query)
                cur.execute(query, (feedback_msg, chat_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            # faudrait une autre exception !
            raise HTTPException(e)


def get_messages_counts():
    with get_db() as conn:
        query = """
        WITH message_intervals AS (
            SELECT 
                user_name,
                scenario_id,
                finished_user_timestamp,
                LAG(finished_user_timestamp) OVER (
                    PARTITION BY user_name, scenario_id ORDER BY finished_user_timestamp
                ) AS previous_timestamp
            FROM public.chat_message
        ), time_diffs AS (
            SELECT 
                user_name,
                scenario_id,
                finished_user_timestamp,
                ROUND(finished_user_timestamp - previous_timestamp) AS time_diff
            FROM message_intervals
            WHERE previous_timestamp IS NOT NULL
        )
        SELECT 
            cm.user_name,
            cm.scenario_id,
            COUNT(*) AS message_count,
            ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY td.time_diff)) AS second_between_messages,
            TO_CHAR(TO_TIMESTAMP(MIN(cm.finished_user_timestamp)), 'DD-MM-YYYY HH24:MI') AS start,
            TO_CHAR(TO_TIMESTAMP(MAX(cm.finished_user_timestamp)), 'DD-MM-YYYY HH24:MI') AS end,
            ROUND((EXTRACT(EPOCH FROM NOW()) - MAX(cm.finished_user_timestamp)) / 60) AS finished_minutes_ago
        FROM public.chat_message cm
        LEFT JOIN time_diffs td 
            ON cm.user_name = td.user_name AND cm.scenario_id = td.scenario_id
        GROUP BY cm.user_name, cm.scenario_id
        ORDER BY finished_minutes_ago ASC NULLS LAST;
        """

        # Exécution de la requête et récupération des résultats dans un DataFrame pandas
        df = pd.read_sql_query(query, conn)

        # Génération du tableau HTML
        html_table = df.to_html(index=True, escape=False, border=1)

        return html_table
