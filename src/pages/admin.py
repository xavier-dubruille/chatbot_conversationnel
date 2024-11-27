from fasthtml.common import *

import apps
from db_utils import create_db, update_system_prompt, get_system_prompt
from state import get_state

app = apps.fast_app


@app.route("/init")
def get():
    create_db()


@dataclass
class Prompt:
    # key: str
    # description: str
    content: str


@app.post("/s/{scenario}/update/{key}")
def update_textarea(scenario: int, key: str, session, prompt: Prompt):
    state = get_state(session)
    state.scenario_id = scenario
    print(state)
    update_system_prompt(scenario, key, prompt.content)
    return Redirect(f"/s/{scenario}/admin")


@app.get("/s/{scenario}/admin")
def get(scenario: int, session):
    state = get_state(session)
    state.scenario_id = scenario
    page = Body(
        Grid(H1(f"Prompts configuration (for scenario num {scenario})", cls="text-2xl font-bold mb-4"),
             Div(A('Back to chat', href=f'/s/{scenario}', cls="text-blue-500 hover:text-blue-700 underline"),
                 style='text-align: right'),
             cls="m-3"),

        Div(
            Div(
                H2("Main prompt (for the role playing)", cls="text-lg mb-2"),
                Form(
                    Textarea(get_system_prompt(scenario, 'role'), name="content", cls="w-full border p-2 mb-4"),
                    Button("Save", type="submit", cls="bg-blue-500 text-white px-4 py-2 rounded"),
                    hx_post=f'/s/{scenario}/update/role'
                ),
                cls="mb-8"
            ),
            Div(
                H2("Tutor's Prompt. (each user prompt is a new conversation starting by this prompt followed by the student's prompt)",
                   cls="text-lg mb-2"),
                Form(
                    Textarea(get_system_prompt(scenario, 'tutor'), name="content", cls="w-full border p-2 mb-4"),
                    Button("Save", type="submit", cls="bg-blue-500 text-white px-4 py-2 rounded"),
                    hx_post=f'/s/{scenario}/update/tutor'
                ),
                cls="mb-8"
            ),
            Div(
                H2("Prompt used to resume all current feedbacks (not yet used)", cls="text-lg mb-2"),
                Form(
                    Textarea(get_system_prompt(scenario, 'resume'), name="content", cls="w-full border p-2 mb-4"),
                    Button("Save", type="submit", cls="bg-blue-500 text-white px-4 py-2 rounded"),
                    hx_post=f'/s/{scenario}/update/resume'
                ),
                cls="mb-8"
            ),
            cls="max-w-lg mx-auto p-4"
        )

    )
    return Title('Administration'), page
