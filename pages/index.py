from fasthtml.common import *

import apps
from db_utils import get_system_prompt, get_create_scenario, get_all_scenario, create_default_system_prompt

app = apps.fast_app
client = apps.client
openAiCli = apps.openAiCli

messages = []
feedback_history = []
current_scenario = 1  # didn't want it but couldn't find a way to pass arguments to the websocket fonction ...


# Chat message component (renders a chat bubble)
# Now with a unique ID for the content and the message
def ChatMessage(msg_idx, **kwargs):
    msg = messages[msg_idx]
    bubble_class = "chat-bubble-primary" if msg['role'] == 'user' else 'chat-bubble-secondary'
    chat_class = "chat-end" if msg['role'] == 'user' else 'chat-start'
    return Div(Div(msg['role'], cls="chat-header"),
               Div(msg['content'],
                   id=f"chat-content-{msg_idx}",  # Target if updating the content
                   cls=f"chat-bubble {bubble_class}"),
               id=f"chat-message-{msg_idx}",  # Target if replacing the whole message
               cls=f"chat {chat_class}", **kwargs)


# The input field for the user message. Also used to clear the
# input field after sending a message via an OOB swap
def ChatInput():
    return Input(type="text", name='msg', id='msg-input',
                 placeholder="Type a message",
                 cls="input input-bordered w-full", hx_swap_oob='true')


def ScenarioButton(scenario):
    return Div(
        A(f"{scenario[1]}(id={scenario[0]})", href=f'/s/{scenario[0]}', cls="btn btn-primary text-2xl font-bold mb-4"))


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


# The main screen
@app.route("/s/{scenario}")
def get(scenario: int):
    global current_scenario
    current_scenario = scenario
    print(f"Current scenario: {current_scenario}")

    global messages
    messages = [{"role": "assistant", "content": "Hello"}]

    senario_name = get_create_scenario(scenario)

    chat_elements = [
        Div(*[ChatMessage(msg_idx) for msg_idx, msg in enumerate(messages)],
            id="chatlist", cls="chat-box h-[73vh] overflow-y-auto"),
        Form(Group(ChatInput(), Button("Send", cls="btn btn-primary")),
             ws_send=True, hx_ext="ws", ws_connect="/wscon",
             cls="flex space-x-2 m-2")]

    page = Body(Grid(H1(senario_name, cls="text-2xl font-bold mb-4", id="titre"),
                     Div(A('Configure Me', href=f'/s/{scenario}/admin',
                           cls="text-blue-500 hover:text-blue-700 underline"),
                         style='text-align: right'),
                     cls="m-3"),
                Div(Div(*chat_elements,
                        cls="card bg-base-300 rounded-box basis-[75%] "),
                    Div(cls="divider divider-horizontal"),
                    Div(H1("Feedback with History", style="position:absolute;top:5px;font-size:29px"),
                        Div("", id="tutor_history_content"),
                        cls='card bg-base-300 rounded-box grid flex-grow place-items-center basis-[35%] grow-0 shrink-0 overflow-y-auto '),
                    Div(cls="divider divider-horizontal"),
                    Div(H1("Feedback No History", style="position:absolute;top:5px;font-size:29px"),
                        Div("", id="tutor_content"),
                        cls='card bg-base-300 rounded-box grid flex-grow place-items-center basis-[35%] grow-0 shrink-0 overflow-y-auto '),
                    cls="flex flex-row w-full p-3")
                )
    return Title(senario_name), page


async def ask_tutor(scenario):
    last_user_content = next(
        (message["content"] for message in reversed(messages) if message["role"] == "user"),
        None
    )

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


async def cli(scenario, messages):
    sp = get_system_prompt(scenario, "role", "You are a funny and useless assistant.")
    messages_to_send = [{"role": "system", "content": sp}] + messages
    stream = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages_to_send,
        stream=True,
    )
    return stream


async def ask_history_tutor(current_scenario):
    global feedback_history

    last_user_content = next(
        (message["content"] for message in reversed(messages) if message["role"] == "user"),
        None
    )

    if last_user_content is None:
        return None, "Start talking with the chatbot first"
    # else
    feedback_history.append({"role": "user", "content": last_user_content})

    sp = get_system_prompt(current_scenario, "tutor", f"Je vais te donner le prompt d'un étudiant et "
                                                      "tu vas me donner un regard critique sur le style , "
                                                      "la grammaire et le vocabulaire utilisé: ")

    completion = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": sp}] + feedback_history,
    )

    responce = completion.choices[0].message.content
    feedback_history.append({"role": "assistant", "content": responce})
    return last_user_content, responce


def render_feedback(last_user_message, feedback, id_to_swap):
    return Div(
        Div(
            Span(last_user_message, cls="rounded-lg px-2",
                 style="position:absolute; top:0; left:0; background:#4a00ff; color:#d1dbff"),
            Div(feedback, cls="max-w-sm mx-auto p-6 bg-pink-100 rounded-lg shadow-lg border border-pink-200 my-2"),
            style="position:relative"
        ),
        hx_swap_oob='beforeend',
        id=id_to_swap
    )


@app.ws('/wscon')
async def ws(msg: str, send):
    messages.append({"role": "user", "content": msg.rstrip()})
    swap = 'beforeend'

    # Send the user message to the user (updates the UI right away)
    await send(Div(ChatMessage(len(messages) - 1), hx_swap_oob=swap, id="chatlist"))

    # Send the clear input field command to the user
    await send(ChatInput())  # todo: it works but we lose focus

    # Model response (streaming)
    r = await cli(current_scenario, messages)

    # Send an empty message with the assistant response
    messages.append({"role": "assistant", "content": ""})
    await send(Div(ChatMessage(len(messages) - 1), hx_swap_oob=swap, id="chatlist"))

    # Fill in the message content
    async for chunk in r:
        delta = chunk.choices[0].delta.content or ""
        messages[-1]["content"] += delta
        await send(Span(delta, id=f"chat-content-{len(messages) - 1}", hx_swap_oob=swap))

    last_user_message, feedback = await ask_tutor(current_scenario)
    feedback_rendered = render_feedback(last_user_message, feedback, "tutor_content")
    await send(feedback_rendered)

    last_user_message, feedback = await ask_history_tutor(current_scenario)
    feedback_rendered = render_feedback(last_user_message, feedback, "tutor_history_content")
    await send(feedback_rendered)
