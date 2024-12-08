import apps
import os

from config import get_scenario_config

app = apps.fast_app
client = apps.client
openAiCli = apps.openAiCli


async def cli(scenario_id, messages):
    scenario_config = get_scenario_config(scenario_id)
    messages_to_send = [{"role": "system", "content": scenario_config.role_prompt}] + messages
    stream = await client.chat.completions.create(
        model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        messages=messages_to_send,
        stream=True,
    )
    return stream
