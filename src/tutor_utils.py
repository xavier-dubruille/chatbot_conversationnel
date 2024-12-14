import markdown
from fasthtml.common import *

import apps
from config import get_scenario_config
from state import State
from litellm_stuff import complete

app = apps.fast_app

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
    """aka feedback 1"""
    scenario_config = get_scenario_config(state.scenario_id)

    completion = await complete(
        model=scenario_config.feedback_1_model,
        system_prompt=scenario_config.feedback_1_prompt,
        messages=[{"role": "user", "content": state.last_user_prompt}],
        temperature=scenario_config.feedback_1_temperature,
    )

    return completion.choices[0].message.content


async def ask_history_tutor(state: State):
    """aka feedback 2"""
    scenario_config = get_scenario_config(state.scenario_id)
    state.tutor_feedbacks.append({"role": "user", "content": state.last_user_prompt})

    completion = await complete(
        model=scenario_config.feedback_2_model,
        system_prompt=scenario_config.feedback_2_prompt,
        messages=state.tutor_feedbacks,
        temperature=scenario_config.feedback_2_temperature,
    )

    response = completion.choices[0].message.content
    state.tutor_feedbacks.append({"role": "assistant", "content": response})
    return response


async def resume_feedback(state: State):
    """aka resume_1 """
    contents = [d["content"] for d in state.tutor_feedbacks if "content" in d and d.get("role") == "assistant"]
    scenario_config = get_scenario_config(state.scenario_id)
    msg = " \n ================ \n".join(contents)
    # print("voici le resume sp: " + sp)

    completion = await complete(
        model=scenario_config.resume_1_model,
        system_prompt=scenario_config.resume_1_prompt,
        messages=[{"role": "user", "content": msg}],
        temperature=scenario_config.resume_1_temperature,
    )

    response = completion.choices[0].message.content
    return response


async def feedback_on_all_messages(state: State):
    """aka resume_2"""
    scenario_config = get_scenario_config(state.scenario_id)
    contents = [d["content"] for d in state.messages if "content" in d and d.get("role") == "user"]
    msg = (" \n ================ \n".join(contents))
    # print(msg)

    completion = await complete(
        model=scenario_config.resume_2_model,
        system_prompt=scenario_config.resume_2_prompt,
        messages=[{"role": "user", "content": msg}],
        temperature=scenario_config.resume_2_temperature,
    )

    response = completion.choices[0].message.content
    return response
