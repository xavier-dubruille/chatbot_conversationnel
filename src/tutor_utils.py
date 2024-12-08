import markdown
from fasthtml.common import *

import apps
from config import get_scenario_config
from state import State

app = apps.fast_app
client = apps.client
openAiCli = apps.openAiCli

ID_FEEDBACK_1 = 'id_feedback_1'
ID_FEEDBACK_2 = 'id_feedback_2'
ID_FEEDBACK_3 = 'id_feedback_3'
ID_FEEDBACK_4 = 'id_feedback_4'


def render_feedback(last_user_message, feedback, id_to_swap, swap_method='beforeend'):
    # feedback_md = NotStr(f'''<zero-md><script type="text/markdown">{feedback}</script></zero-md>''')
    feedback_md = NotStr(markdown.markdown(feedback))
    return Div(
        Div(
            Span(last_user_message, cls="rounded-lg px-2",
                 style="position:absolute; top:0; left:0; background:#4a00ff; color:#d1dbff"),
            Div(feedback_md, cls="max-w-sm mx-auto p-6 bg-pink-100 rounded-lg shadow-lg border border-pink-200 my-2"),
            style="position:relative"
        ),
        hx_swap_oob=swap_method,
        id=id_to_swap
    )


async def ask_tutor(state: State):
    scenario_config = get_scenario_config(state.scenario_id)

    completion = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": scenario_config.feedback_1_prompt},
            {
                "role": "user",
                "content": state.last_user_prompt
            }
        ]
    )

    return completion.choices[0].message.content


async def ask_history_tutor(state: State):
    scenario_config = get_scenario_config(state.scenario_id)
    state.tutor_feedbacks.append({"role": "user", "content": state.last_user_prompt})

    completion = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": scenario_config.feedback_2_prompt}] + state.tutor_feedbacks,
    )

    responce = completion.choices[0].message.content
    state.tutor_feedbacks.append({"role": "assistant", "content": responce})
    return responce


async def resume_feedback(state: State):
    contents = [d["content"] for d in state.tutor_feedbacks if "content" in d and d.get("role") == "assistant"]
    scenario_config = get_scenario_config(state.scenario_id)
    msg = " \n ================ \n".join(contents)
    # print("voici le resume sp: " + sp)

    completion = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": scenario_config.resume_1_prompt},
                  {"role": "user", "content": msg}]
    )

    response = completion.choices[0].message.content
    return response


async def feedback_on_all_messages(state: State):
    scenario_config = get_scenario_config(state.scenario_id)
    contents = [d["content"] for d in state.messages if "content" in d and d.get("role") == "user"]
    msg = (" \n ================ \n".join(contents))
    # print(msg)

    completion = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": scenario_config.resume_2_prompt}, {"role": "user", "content": msg}]
    )

    response = completion.choices[0].message.content
    return response
