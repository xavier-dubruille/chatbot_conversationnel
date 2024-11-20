import sqlite3

DB_FILE = "system_prompts.db"
prompt_keys = {'role', 'tutor', 'resume'}


def create_db():
    # manually delete DB_FILE if you want to update
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()

    cur.execute("CREATE TABLE system_prompt(scenario, what, description, content)")
    cur.execute("""CREATE TABLE scenario (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT NOT NULL,
                   created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
                """)

    con.commit()
    con.close()

    create_default_system_prompt(1)


def get_create_scenario(scenario: int):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    res = cur.execute(f"SELECT name FROM scenario WHERE id={scenario}")
    one = res.fetchone()
    con.close()
    if one is not None:
        return one[0]

    # else
    create_default_system_prompt(scenario)
    return get_create_scenario(scenario)


def get_system_prompt(scenario, what, default_prompt="you are a helpful assistant"):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    stm = f"SELECT content FROM system_prompt WHERE what='{what}' and scenario={scenario}"
    # print(stm)
    res = cur.execute(stm)
    one = res.fetchone()
    con.close()
    return one[0] if one else default_prompt


def get_all_scenario():
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    stm = f"SELECT * FROM scenario"
    # print(stm)
    res = cur.execute(stm)
    all = res.fetchall()
    con.close()
    return all


def update_system_prompt(scenario, what, prompt):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("update system_prompt set content = ? where what = ? and scenario = ?",
                (prompt, what, scenario))
    con.commit()
    con.close()


def create_default_system_prompt(scenario_id=-1, scenario_name="Chat with me"):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    id = scenario_id

    if scenario_id < 0:
        cur.execute(f"INSERT INTO scenario(name) VALUES ('{scenario_name}') ")
        id = cur.lastrowid
    else:
        cur.execute(f"INSERT INTO scenario(id, name) VALUES ({scenario_id}, '{scenario_name}') ")

    cur.execute(f"""INSERT INTO system_prompt VALUES
            ({id}, 'role', '', "Tu es un assistant déprimé et antimatique"),
            ({id}, 'tutor', '',"fait un feedback inutile sur ce prompt:"),
            ({id}, 'resume', '',"") """)
    con.commit()
    con.close()
    return id
