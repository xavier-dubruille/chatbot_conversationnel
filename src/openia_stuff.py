import apps
from db_utils import get_system_prompt

app = apps.fast_app
client = apps.client
openAiCli = apps.openAiCli


async def cli(scenario, messages):
    sp = get_system_prompt(scenario, "role", "You are a funny and useless assistant.")
    messages_to_send = [{"role": "system", "content": sp}] + messages
    stream = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages_to_send,
        stream=True,
    )
    return stream
