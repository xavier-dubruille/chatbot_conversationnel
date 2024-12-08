from scenario_config import ScenarioConfig
from scenario_to_db import get_all_scenarios

_config = {}  # dict of Config.  first key is scenario,


def _reset_config():
    global _config
    _config = {}
    for scenario in get_all_scenarios():
        _config[scenario.id] = scenario


def get_scenario_config(scenario_id: int, force_update=False) -> ScenarioConfig:
    if force_update or scenario_id not in _config:
        _reset_config()
    return _config[scenario_id]


def get_all_scenario_config(force_update=False):
    if force_update or len(_config) == 0:
        _reset_config()
    return _config
