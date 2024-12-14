from fasthtml.common import *

import apps
from config import get_scenario_config
from scenario_config import create_exemple_scenario_config, get_attribute_descriptions, Category
from scenario_to_db import create_scenario_table, insert_scenario, update_scenario, ScenarioConfig
from state import get_state
from litellm_stuff import models

app = apps.fast_app


@app.route("/admin/init_db")
def get():
    create_scenario_table()
    insert_scenario(create_exemple_scenario_config())
    return Redirect("/")


@app.post("/s/{scenario_id}/update")
def update_scenario_config(scenario_id: int, scenario: ScenarioConfig):
    scenario.id = scenario_id
    update_scenario(scenario)
    return Redirect(f"/s/{scenario_id}/admin")


def make_config_line(key: str, description: str, scenario: ScenarioConfig):
    if key == "id":
        return Div()
    
    if key.endswith("_model"):
        options = [Option(model, selected = model == getattr(scenario, key)) for model in models.list()]
        input = Select(
            *options,
            name=key,
            cls="border-gray-300 rounded-lg p-2 w-full focus:ring focus:ring-indigo-300 col-span-2")
    else:
        input = Textarea(
            getattr(scenario, key),
            value=getattr(scenario, key),
            placeholder="Enter value",
            type="text",
            name=key,
            style={"height": "100%"},
            cls="border-gray-300 rounded-lg p-2 w-full focus:ring focus:ring-indigo-300 col-span-2")
        
    return Div(
        Label(key, cls="font-medium text-gray-600 col-span-1"),
        Span(description, cls="text-gray-500 col-span-1"),
        input,
        cls="grid grid-cols-4 gap-4 items-center border-b pb-4")


def Accordion(title="", content=Div(), is_checked=False):
    return Div(
        Input(type='radio', name='my-accordion-2', checked=is_checked),
        Div(title, cls="collapse-title text-xl font-medium"),
        Div(content, cls="collapse-content"),
        cls="collapse collapse-arrow bg-base-200"
    )


@app.get("/s/{scenario_id}/admin")
def get(scenario_id: int, session):
    state = get_state(session)
    state.scenario_id = scenario_id
    scenario_config = get_scenario_config(state.scenario_id, True)
    script_color_dirty = NotStr("""  <script>
    document.querySelectorAll('#dynamicForm textarea').forEach(
      input => {
        input.addEventListener('input', () => { input.classList.add('bg-yellow-100', 'border-yellow-500'); 
      });
    });
  </script>""")
    page = Body(
        Div(
            Div(H1(f"Configuration (for Scenario '{scenario_id}')", cls="text-2xl font-bold text-gray-700 mb-6"),
                Div(A('Back to chat', href=f'/s/{scenario_id}',
                      cls="text-blue-500 hover:text-blue-700 underline"),
                    style='text-align: right'),
                Form(
                    Accordion("'General' configurations",
                              Div(*[make_config_line(k, v, scenario_config) for k, v in
                                    get_attribute_descriptions(Category.MAIN)]), True),
                    Accordion("'Role' configurations",
                              Div(*[make_config_line(k, v, scenario_config) for k, v in
                                    get_attribute_descriptions(Category.ROLE)])),
                    Accordion("First 'Feedback window' configurations",
                              Div(*[make_config_line(k, v, scenario_config) for k, v in
                                    get_attribute_descriptions(Category.FEEDBACK1)])),
                    Accordion("Second 'Feedback window' configurations",
                              Div(*[make_config_line(k, v, scenario_config) for k, v in
                                    get_attribute_descriptions(Category.FEEDBACK2)])),
                    Accordion("First 'Resume window' configurations",
                              Div(*[make_config_line(k, v, scenario_config) for k, v in
                                    get_attribute_descriptions(Category.RESUME1)])),
                    Accordion("Second 'Resume window' configurations",
                              Div(*[make_config_line(k, v, scenario_config) for k, v in
                                    get_attribute_descriptions(Category.RESUME2)])),

                    Div(Button("Save", type="submit",
                               cls="bg-indigo-600 text-white font-bold px-6 py-2 rounded-lg shadow-md hover:bg-indigo-700 transition"),
                        cls="mt-6 text-right"),
                    id="dynamicForm",
                    cls="space-y-4",
                    sytle={"margin-top": "50px"},
                    hx_post=f'/s/{scenario_id}/update'
                )
                ),
            cls="bg-white shadow-md rounded-lg p-6 max-w-7xl w-full"
        ),
        script_color_dirty,
        cls="bg-gray-100 min-h-screen flex items-center justify-center"
    )
    return page
