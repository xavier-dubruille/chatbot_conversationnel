from dataclasses import replace

from fasthtml.common import *

import apps
from config import get_all_scenario_config, get_scenario_config
from scenario_config import ScenarioConfig
from scenario_to_db import *
from state import get_state

app = apps.fast_app


@dataclass
class Scenario:
    name: str


@app.route("/s/{scenario_id}/copy")
def get(scenario_id: int):
    origin_scenario = get_scenario_config(scenario_id)
    new_scenario = replace(origin_scenario, scenario_name=f"Copy of: {origin_scenario.scenario_name}")
    insert_scenario(new_scenario)  # don't worry: the 'origin' id isn't inserted (so it will be auto incremented by DB)
    return Redirect("/")


@app.route("/s/{scenario_id}/delete")
def get(scenario_id: int):
    delete_scenario(ScenarioConfig(id=scenario_id))
    return Redirect("/")


@app.route("/")
def get(session):
    get_state(session).scenario_id = 0

    all_scenarios = get_all_scenario_config(True)
    # print(all_scenarios)
    page = Body(
        Div(*[ScenarioButton(scenario, len(all_scenarios) == 1) for scenario in all_scenarios.values()],
            cls="flex flex-col items-center justify-center h-screen bg-gray-100")
    )
    return Title("Scenario"), page


def ScenarioButton(scenario: ScenarioConfig, no_delete_button=False):
    return Div(
        A(f"{scenario.scenario_name}",
          href=f'/s/{scenario.id}',
          style="width: 700px",
          cls="btn btn-primary text-2xl font-bold mb-4"),
        I(hx_get=f"/s/{scenario.id}/copy",
          title="Copy this Scenario",
          cls="fa-solid fa-copy",
          style={"font-size": "2rem", "padding": "15px", "margin-left": "15px"}),
        Div() if no_delete_button else
        I(cls='fa-solid fa-trash', alt="Delete me", hx_get=f"/s/{scenario.id}/delete",
          title="Delete this Scenario",
          style={"font-size": "2rem", "padding": "15px", "margin-left": "15px"}),
    )
