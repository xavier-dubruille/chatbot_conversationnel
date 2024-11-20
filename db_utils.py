import sqlite3

DB_FILE = "system_prompts.db"
prompt_keys = {'role', 'tutor', 'resume'}


def create_db():
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("CREATE TABLE system_prompt(what, prompt)")
    cur.execute("""INSERT INTO system_prompt VALUES
            ('role', "Tu es un assistant déprimé et antimatique"),
            ('tutor', "fait un feedback inutile sur ce prompt: {prompt}"),
            ('resume', "") """)
    con.commit()


def get_system_prompt(what, default_prompt="you are a helpful assistant"):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    res = cur.execute(f"SELECT prompt FROM system_prompt WHERE what='{what}'")
    one = res.fetchone()
    return one[0] if one else default_prompt


def update_system_prompt(what, prompt):
    # todo: escape single/double cote !
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute(f"update system_prompt set prompt = '{prompt}' where what = '{what}'")
    con.commit()
