from fasthtml.common import *

import apps
from config import KEY_DESCRIPTION
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
                H2("Prompt used to resume all current feedbacks", cls="text-lg mb-2"),
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


def make_config_line(k: str, v: str):
    return Div(
        Label(k, cls="font-medium text-gray-600"),
        Span(v, cls="text-gray-500"),
        Input(placeholder="Enter value",
              cls="border-gray-300 rounded-lg p-2 w-full focus:ring focus:ring-indigo-300"),
        cls="grid grid-cols-3 gap-4 items-center border-b pb-4")


@app.get('/admin/')
def test():
    script_color_dirty = NotStr("""  <script>
    document.querySelectorAll('#dynamicForm input').forEach(input => {
      input.addEventListener('input', () => {
        input.classList.add('bg-yellow-100', 'border-yellow-500');
      });
    });
  </script>""")
    page = Body(
        Div(
            Div(H1("Configuration", cls="text-2xl font-bold text-gray-700 mb-6"),
                Form(
                    *[make_config_line(k, v) for k, v in KEY_DESCRIPTION.items()],
                    Div(Button("Save", type="submit",
                               cls="bg-indigo-600 text-white font-bold px-6 py-2 rounded-lg shadow-md hover:bg-indigo-700 transition"),
                        cls="mt-6 text-right"),
                    id="dynamicForm", cls="space-y-4"
                )),
            cls="bg-white shadow-md rounded-lg p-6 max-w-2xl w-full"
        ),
        script_color_dirty,
        cls="bg-gray-100 min-h-screen flex items-center justify-center"
    )
    return page


@app.get('/test2/')
def test2():
    raw_content = """
<body class="bg-gray-100 min-h-screen flex items-center justify-center">
  <div class="bg-white shadow-md rounded-lg p-6 max-w-2xl w-full">
    <h1 class="text-2xl font-bold text-gray-700 mb-6">Formulaire</h1>
    <form id="dynamicForm" class="space-y-4">
      
      <!-- Ligne 1 -->
      <div class="grid grid-cols-3 gap-4 items-center border-b pb-4">
        <label class="font-medium text-gray-600">Code 1</label>
        <span class="text-gray-500">Description 1</span>
        <input 
          type="text" 
          placeholder="Entrez une valeur"
          class="border-gray-300 rounded-lg p-2 w-full focus:ring focus:ring-indigo-300"
        />
      </div>

      <!-- Ligne 2 -->
      <div class="grid grid-cols-3 gap-4 items-center border-b pb-4">
        <label class="font-medium text-gray-600">Code 2</label>
        <span class="text-gray-500">Description 2</span>
        <input 
          type="text" 
          placeholder="Entrez une valeur"
          class="border-gray-300 rounded-lg p-2 w-full focus:ring focus:ring-indigo-300"
        />
      </div>

      <!-- Ligne 3 -->
      <div class="grid grid-cols-3 gap-4 items-center border-b pb-4">
        <label class="font-medium text-gray-600">Code 3</label>
        <span class="text-gray-500">Description 3</span>
        <input 
          type="text" 
          placeholder="Entrez une valeur"
          class="border-gray-300 rounded-lg p-2 w-full focus:ring focus:ring-indigo-300"
        />
      </div>

      <!-- Ligne 4 -->
      <div class="grid grid-cols-3 gap-4 items-center">
        <label class="font-medium text-gray-600">Code 4</label>
        <span class="text-gray-500">Description 4</span>
        <input 
          type="text" 
          placeholder="Entrez une valeur"
          class="border-gray-300 rounded-lg p-2 w-full focus:ring focus:ring-indigo-300"
        />
      </div>

      <!-- Bouton Save -->
      <div class="mt-6 text-right">
        <button 
          type="submit"
          class="bg-indigo-600 text-white font-bold px-6 py-2 rounded-lg shadow-md hover:bg-indigo-700 transition">
          Save
        </button>
      </div>

    </form>
  </div>

  <script>
    // Sélectionner tous les champs d'entrée du formulaire
    document.querySelectorAll('#dynamicForm input').forEach(input => {
      input.addEventListener('input', () => {
        // Ajouter une classe si le champ a été modifié
        input.classList.add('bg-yellow-100', 'border-yellow-500');
      });
    });
  </script>
</body>

    """
    return Div(NotStr(raw_content))
