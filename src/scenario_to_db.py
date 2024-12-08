import sqlite3
from dataclasses import fields, asdict
from functools import wraps

from scenario_config import ScenarioConfig


# Décorateur pour gérer la connexion à la base de données
def _with_db(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect("scenario_configs.db")
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()  # Commit après l'exécution de la fonction
            return result
        finally:
            conn.close()

    return wrapper


@_with_db
def create_scenario_table(conn):
    table_name = ScenarioConfig.__name__.lower()
    columns = ", ".join(
        f"{field.name} {_get_sql_type(field.type)}" + (" PRIMARY KEY AUTOINCREMENT" if field.name == "id" else "")
        for field in fields(ScenarioConfig)
    )
    sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
    conn.execute(sql)


# Fonction pour mapper les types Python aux types SQL
def _get_sql_type(py_type):
    if py_type == int:
        return "INTEGER"
    elif py_type == float:
        return "REAL"
    elif py_type == str:
        return "TEXT"
    else:
        return "TEXT"


@_with_db
def insert_scenario(conn, scenario: ScenarioConfig):
    table_name = scenario.__class__.__name__.lower()
    obj_dict = asdict(scenario)
    obj_dict.pop("id")
    columns = ", ".join(obj_dict.keys())
    placeholders = ", ".join(["?" for _ in obj_dict])
    values = list(obj_dict.values())
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    cursor = conn.cursor()
    cursor.execute(sql, values)
    scenario.id = cursor.lastrowid  # Met à jour l'ID de l'objet si c'est une clé primaire auto-incrémentée
    return scenario


@_with_db
def get_all_scenarios(conn):
    table_name = ScenarioConfig.__name__.lower()
    sql = f"SELECT * FROM {table_name}"
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    return [ScenarioConfig(**dict(zip([field.name for field in fields(ScenarioConfig)], row))) for row in rows]


@_with_db
def update_scenario(conn, scenario: ScenarioConfig):
    table_name = scenario.__class__.__name__.lower()
    obj_dict = asdict(scenario)
    obj_id = obj_dict.pop("id")
    set_clause = ", ".join([f"{key} = ?" for key in obj_dict.keys()])
    values = list(obj_dict.values())
    values.append(obj_id)
    sql = f"UPDATE {table_name} SET {set_clause} WHERE id = ?"
    return conn.execute(sql, values)  # todo: return if it has been updated


@_with_db
def delete_scenario(conn, scenario: ScenarioConfig):
    table_name = scenario.__class__.__name__.lower()
    sql = f"DELETE FROM {table_name} WHERE id = ?"
    conn.execute(sql, (scenario.id,))
