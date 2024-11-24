from fasthtml.common import *

from src import apps
from src.db_utils import get_create_scenario
from src.openia_stuff import cli
from src.tutor_utils import render_feedback, ask_tutor, ask_history_tutor, feedback_on_all_messages, resume_feedback

app = apps.fast_app
client = apps.client
openAiCli = apps.openAiCli

current_scenario = 1  # didn't want it but couldn't find a way to pass arguments to the websocket fonction ...

ID_FEEDBACK_1 = 'id_feedback_1'
ID_FEEDBACK_2 = 'id_feedback_2'
ID_FEEDBACK_3 = 'id_feedback_3'
ID_FEEDBACK_4 = 'id_feedback_4'


# Chat message component (renders a chat bubble)
# Now with a unique ID for the content and the message
def ChatMessage(msg_idx, **kwargs):
    msg = apps.messages[msg_idx]
    bubble_class = "chat-bubble-primary" if msg['role'] == 'user' else 'chat-bubble-secondary bg-fuchsia-600'
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


# The main screen
@app.route("/s/{scenario}")
def get(scenario: int):
    global current_scenario
    current_scenario = scenario
    print(f"Current scenario: {current_scenario}")

    apps.messages = [{"role": "assistant", "content": "Hello"}]

    senario_name = get_create_scenario(scenario)

    chat_elements = [
        Div(*[ChatMessage(msg_idx) for msg_idx, msg in enumerate(apps.messages)],
            id="chatlist", cls="chat-box h-[73vh] overflow-y-auto"),
        Form(Group(ChatInput(), Button("Send", cls="btn btn-primary")),
             ws_send=True, hx_ext="ws", ws_connect="/wscon",
             cls="flex space-x-2 m-2")]

    sub_title_style = "position:relative; margin:8px; font-size:29px"

    page = Body(Grid(H1(A(senario_name, href=f'/'), cls="text-2xl font-bold mb-4", id="titre"),
                     Div(A('Configure Me', href=f'/s/{scenario}/admin',
                           cls="text-blue-500 hover:text-blue-700 underline"),
                         style='text-align: right'),
                     cls="m-3"),
                Div(Div(*chat_elements,
                        cls="card bg-base-300 rounded-box basis-[75%] "),
                    Div(cls="divider divider-horizontal"),

                    Div(Div(H1("Feedback with History", style=sub_title_style),
                            Div("", id="tutor_history_content"),
                            cls='card bg-base-300 rounded-box ',
                            style="width:100%; height:100%"
                            ),
                        Div(cls="divider divider-vertical"),
                        Div(H1("Summary all messages", style=sub_title_style),
                            Div("", id=ID_FEEDBACK_3),
                            cls='card bg-base-300 rounded-box',
                            style="width:100%; height:100%"
                            ),
                        cls='grid flex-grow place-items-center basis-[35%] grow-0 shrink-0 overflow-y-auto ',
                        style='display: flex; flex-direction: column; justify-content: center'
                        ),

                    Div(cls="divider divider-horizontal"),
                    Div(Div(H1("Feedback No History", style=sub_title_style),
                            Div("", id="tutor_content"),
                            cls='card bg-base-300 rounded-box ',
                            style="width:100%; height:100%"
                            ),
                        Div(cls="divider divider-vertical"),
                        Div(H1("Summary all feedbacks", style=sub_title_style),
                            Div("", id=ID_FEEDBACK_4),
                            cls='card bg-base-300 rounded-box',
                            style="width:100%; height:100%"
                            ),
                        cls='grid flex-grow place-items-center basis-[35%] grow-0 shrink-0 overflow-y-auto ',
                        style='display: flex; flex-direction: column; justify-content: center'
                        ),

                    cls="flex flex-row w-full p-3")
                )
    return Title(senario_name), page


@app.ws('/wscon')
async def ws(msg: str, send):
    apps.messages.append({"role": "user", "content": msg.rstrip()})
    swap = 'beforeend'

    # Send the user message to the user (updates the UI right away)
    await send(Div(ChatMessage(len(apps.messages) - 1), hx_swap_oob=swap, id="chatlist"))

    # Send the clear input field command to the user
    await send(ChatInput())  # todo: it works but we lose focus

    # Model response (streaming)
    r = await cli(current_scenario, apps.messages)

    # Send an empty message with the assistant response
    apps.messages.append({"role": "assistant", "content": ""})
    await send(Div(ChatMessage(len(apps.messages) - 1), hx_swap_oob=swap, id="chatlist"))

    # Fill in the message content
    async for chunk in r:
        delta = chunk.choices[0].delta.content or ""
        apps.messages[-1]["content"] += delta
        await send(Span(delta, id=f"chat-content-{len(apps.messages) - 1}", hx_swap_oob=swap))

    last_user_message, feedback = await ask_tutor(current_scenario)
    feedback_rendered = render_feedback(last_user_message, feedback, "tutor_content")
    await send(feedback_rendered)

    last_user_message, feedback = await ask_history_tutor(current_scenario)
    feedback_rendered = render_feedback(last_user_message, feedback, "tutor_history_content")
    await send(feedback_rendered)

    last_user_message, feedback = await feedback_on_all_messages(current_scenario)
    feedback_rendered = render_feedback("last: " + last_user_message, feedback, ID_FEEDBACK_3, 'true')
    await send(feedback_rendered)

    last_user_message, feedback = await resume_feedback(current_scenario)
    feedback_rendered = render_feedback("last: " + last_user_message, feedback, ID_FEEDBACK_4, 'true')
    await send(feedback_rendered)
