from fasthtml.common import *

import apps
from db_utils import create_db, update_system_prompt, get_system_prompt

app = apps.fast_app


@app.route("/init")
def get():
    create_db()


@dataclass
class Prompt:
    # key: str
    # description: str
    content: str


@app.post("/update/{key}")
def update_textarea(key: str, prompt: Prompt):
    update_system_prompt(key, prompt.content)
    return Redirect("/admin")


@app.get("/admin")
def get():
    page = Body(
        H1("Prompts configuration", cls="text-2xl font-bold mb-4"),
        Div(
            Div(
                H2("Main prompt (for the role playing)", cls="text-lg mb-2"),
                Form(
                    Textarea(get_system_prompt('role'), name="content", cls="w-full border p-2 mb-4"),
                    Button("Save", type="submit", cls="bg-blue-500 text-white px-4 py-2 rounded"),
                    hx_post='/update/role'
                ),
                cls="mb-8"
            ),
            Div(
                H2("Tutor's Prompt. (each user prompt is a new conversation starting by this prompt followed by the student's prompt)", cls="text-lg mb-2"),
                Form(
                    Textarea(get_system_prompt('tutor'), name="content", cls="w-full border p-2 mb-4"),
                    Button("Save", type="submit", cls="bg-blue-500 text-white px-4 py-2 rounded"),
                    hx_post='/update/tutor'
                ),
                cls="mb-8"
            ),
            Div(
                H2("Prompt used to resume all current feedbacks (not yet used)", cls="text-lg mb-2"),
                Form(
                    Textarea(get_system_prompt('resume'), name="content", cls="w-full border p-2 mb-4"),
                    Button("Save", type="submit", cls="bg-blue-500 text-white px-4 py-2 rounded"),
                    hx_post='/update/resume'
                ),
                cls="mb-8"
            ),
            cls="max-w-lg mx-auto p-4"
        )

    )
    return Title('Administration'), page
