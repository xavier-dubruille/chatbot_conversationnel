import markdown
from fasthtml.common import *

from src import apps
from src.db_utils import get_system_prompt

app = apps.fast_app
client = apps.client
openAiCli = apps.openAiCli

current_scenario = 1  # didn't want it but couldn't find a way to pass arguments to the websocket fonction ...

ID_FEEDBACK_1 = 'id_feedback_1'
ID_FEEDBACK_2 = 'id_feedback_2'
ID_FEEDBACK_3 = 'id_feedback_3'
ID_FEEDBACK_4 = 'id_feedback_4'


def get_last_user_msg():
    return next(
        (message["content"] for message in reversed(apps.messages) if message["role"] == "user"),
        None
    )


async def ask_tutor(scenario):
    last_user_content = get_last_user_msg()

    if last_user_content is None:
        return None, "Start talking with the chatbot first"

    sp = get_system_prompt(scenario, "tutor", f"Je vais te donner le prompt d'un étudiant et "
                                              "tu vas me donner un regard critique sur le style , "
                                              "la grammaire et le vocabulaire utilisé: ")

    completion = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": sp},
            {
                "role": "user",
                "content": last_user_content
            }
        ]
    )

    return last_user_content, completion.choices[0].message.content


async def ask_history_tutor(current_scenario):
    last_user_content = get_last_user_msg()

    if last_user_content is None:
        return None, "Start talking with the chatbot first"
    # else
    apps.feedback_history.append({"role": "user", "content": last_user_content})

    sp = get_system_prompt(current_scenario, "tutor", f"Je vais te donner le prompt d'un étudiant et "
                                                      "tu vas me donner un regard critique sur le style , "
                                                      "la grammaire et le vocabulaire utilisé: ")

    completion = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": sp}] + apps.feedback_history,
    )

    responce = completion.choices[0].message.content
    apps.feedback_history.append({"role": "assistant", "content": responce})
    return last_user_content, responce


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


async def resume_feedback(current_scenario):
    last_user_content = get_last_user_msg()

    contents = [d["content"] for d in apps.feedback_history if "content" in d and d.get("role") == "assistant"]
    msg = "fait moi un résumé de tous ces feedbacks: \n " + " \n ================ \n".join(contents)
    # print(msg)

    completion = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": msg}]
    )

    response = completion.choices[0].message.content
    return last_user_content, response


async def feedback_on_all_messages(current_scenario):
    last_user_content = get_last_user_msg()

    contents = [d["content"] for d in apps.messages if "content" in d and d.get("role") == "user"]
    msg = ("fait moi un feedback (orthographe, grammaire et style) sur tous ces messages: \n "
           + " \n ================ \n".join(contents))
    # print(msg)

    completion = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": msg}]
    )

    response = completion.choices[0].message.content
    return last_user_content, response
