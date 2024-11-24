from fasthtml.common import *

from src import apps
from src.db_utils import get_all_scenario, create_default_system_prompt

app = apps.fast_app


@dataclass
class Scenario:
    name: str


@app.route("/new_scenario")
def post(scenario: Scenario):
    id = create_default_system_prompt(scenario_name=scenario.name)
    return Redirect(f"/s/{id}")


@app.route("/")
def get():
    all_scenarios = get_all_scenario()
    # print(all_scenarios)
    page = Body(
        Div(*[ScenarioButton(scenario) for scenario in all_scenarios],
            Form(Group(
                Input("New Scenario", type="text", placeholder='Chat with me', name="name"),
                Button("Save", type="submit", cls="bg-blue-500 text-white px-4 py-2 rounded")),
                cls="x",
                hx_post='/new_scenario'
            ),
            cls="flex flex-col items-center justify-center h-screen bg-gray-100")
    )
    return Title("Scenario"), page


def ScenarioButton(scenario):
    return Div(
        A(f"{scenario[1]}(id={scenario[0]})", href=f'/s/{scenario[0]}', cls="btn btn-primary text-2xl font-bold mb-4"))
