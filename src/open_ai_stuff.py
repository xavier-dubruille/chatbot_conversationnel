import apps
import os

from config import get_scenario_config

app = apps.fast_app
client = apps.client
openAiCli = apps.openAiCli


async def cli(scenario_id, messages):
    # aka role  # todo: this section, along with the scenario_utils should be cleaned, dried and moved
    scenario_config = get_scenario_config(scenario_id)
    role_model = "gpt-4o-mini" if scenario_config.role_model == "gpt4o-mini" \
        else "gpt-4o" if scenario_config.role_model == "gpt4o" \
        else scenario_config.role_model
    messages_to_send = [{"role": "system", "content": scenario_config.role_prompt}] + messages
    stream = await client.chat.completions.create(
        model=role_model,
        temperature=float(scenario_config.role_temperature),
        messages=messages_to_send,
        stream=True,
    )
    return stream
