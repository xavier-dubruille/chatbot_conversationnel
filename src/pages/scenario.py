from fasthtml.common import *

import time
import apps
from config import *
from connected_user import ConnectedUser
from open_ai_stuff import cli
# from open-ai_stuff import ++++++
from state import get_state
from tutor_utils import render_feedback, ask_tutor, ask_history_tutor, feedback_on_all_messages, resume_feedback

current_timestamp = int(time.time())
app = apps.fast_app
client = apps.client
openAiCli = apps.openAiCli

ID_FEEDBACK_1 = 'id_feedback_1'
ID_FEEDBACK_2 = 'id_feedback_2'
ID_FEEDBACK_3 = 'id_feedback_3'
ID_FEEDBACK_4 = 'id_feedback_4'


# Chat message component (renders a chat bubble)
# Now with a unique ID for the content and the message
def ChatMessage(msg_idx, msg, bot_name: str, append_this='', **kwargs):
    bubble_class = "chat-bubble-primary" if msg['role'] == 'user' else 'chat-bubble-secondary bg-fuchsia-600'
    chat_class = "chat-end" if msg['role'] == 'user' else 'chat-start'
    who = bot_name if msg['role'] == 'assistant' else msg['role']
    return Div(Div(who, cls="chat-header"),
               Div(msg['content'] + append_this,
                   id=f"chat-content-{msg_idx}",  # Target if updating the content
                   cls=f"chat-bubble {bubble_class}"),
               id=f"chat-message-{msg_idx}",  # Target if replacing the whole message
               cls=f"chat {chat_class}", **kwargs)


# The input field for the user message. Also used to clear the
# input field after sending a message via an OOB swap
def ChatInput():
    return Input(type="text", name='msg', id='msg-input', autofocus=True,
                 placeholder="Type a message",
                 cls="input input-bordered w-full", hx_swap_oob='true')


# The main screen
@app.route("/s/{scenario_id}")
def get(scenario_id: int, session, request):
    state = get_state(session)
    state.scenario_id = scenario_id
    user = ConnectedUser(request)

    scenario_config: ScenarioConfig = get_scenario_config(scenario_id, True)

    state.messages = [{"role": "assistant", "content": scenario_config.bot_first_msg}]
    state.tutor_feedbacks = []

    chat_elements = [
        Div(*[ChatMessage(msg_idx, msg, scenario_config.bot_name) for msg_idx, msg in enumerate(state.messages)],
            id="chatlist", cls="chat-box h-[73vh] overflow-y-auto"),
        Form(
            Group(
                Div(ChatInput(), id='msg-input-wrapper'),
                Button("Send", id="send_input", cls="btn btn-primary"),
                cls="flex space-x-2 m-2"
            ),
            ws_send=True, hx_ext="ws", ws_connect="/wscon",
            cls="flex space-x-2 m-2")]

    sub_title_style = "position:relative; margin:8px; font-size:29px"

    page = Body(Grid(H1(A(scenario_config.scenario_name, href='/'), cls="text-2xl font-bold mb-4", id="titre"),
                     Div() if user.is_student else Div(A('Configure Me', href=f'/s/{scenario_id}/admin',
                                                         cls="text-blue-500 hover:text-blue-700 underline"),
                                                       style='text-align: right'),
                     cls="m-3"),
                Div(Div(*chat_elements,
                        cls="card bg-base-300 rounded-box basis-[75%] "),
                    Div(cls="divider divider-horizontal"),

                    Div(Div(H1("Tutor (deactivated)", style=sub_title_style),
                            Div("", id="tutor_history_content"),
                            cls='card bg-base-300 rounded-box ',
                            style="width:100%; height:100%"
                            ),
                        # Div(cls="divider divider-vertical"),
                        # Div(H1("Summary all messages", style=sub_title_style),
                        #     Div("", id=ID_FEEDBACK_3),
                        #     cls='card bg-base-300 rounded-box',
                        #     style="width:100%; height:100%"
                        #     ),
                        cls='grid flex-grow place-items-center basis-[35%] grow-0 shrink-0 overflow-y-auto ',
                        style='display: flex; flex-direction: column; justify-content: center'
                        ),

                    # Div(cls="divider divider-horizontal"),
                    # Div(Div(H1("Feedback No History", style=sub_title_style),
                    #         Div("", id="tutor_content"),
                    #         cls='card bg-base-300 rounded-box ',
                    #         style="width:100%; height:100%"
                    #         ),
                    #     Div(cls="divider divider-vertical"),
                    #     Div(H1("Summary all feedbacks", style=sub_title_style),
                    #         Div("", id=ID_FEEDBACK_4),
                    #         cls='card bg-base-300 rounded-box',
                    #         style="width:100%; height:100%"
                    #         ),
                    #     cls='grid flex-grow place-items-center basis-[35%] grow-0 shrink-0 overflow-y-auto ',
                    #     style='display: flex; flex-direction: column; justify-content: center'
                    #     ),

                    cls="flex flex-row w-full p-3")
                )
    return Title(scenario_config.scenario_name), page


@app.ws('/wscon')
async def ws(msg: str, send, scope):
    global current_timestamp
    next_timestamp = int(time.time())

    state = get_state(scope.session)
    scenario_config: ScenarioConfig = get_scenario_config(state.scenario_id)

    state.messages.append({"role": "user", "content": msg.rstrip()})
    swap = 'beforeend'

    # Send the user message to the user (updates the UI right away)
    idx = len(state.messages) - 1
    msg = state.messages[idx]
    # await send(Div(ChatMessage(idx, msg, scenario_config.bot_name, f"  -- ({next_timestamp - current_timestamp}s)"),
    #                hx_swap_oob=swap, id="chatlist"))
    await send(Div(ChatMessage(idx, msg, scenario_config.bot_name),
                   hx_swap_oob=swap, id="chatlist"))

    # Send the clear input field command to the user
    await send(ChatInput())  # todo: it works but we lose focus

    # Model response (streaming)
    r = await cli(state.scenario_id, state.messages)

    # Send an empty message with the assistant response
    state.messages.append({"role": "assistant", "content": ""})
    idx = len(state.messages) - 1
    msg = state.messages[idx]
    await send(Div(ChatMessage(idx, msg, scenario_config.bot_name), hx_swap_oob=swap, id="chatlist"))

    # Fill in the message content
    async for chunk in r:
        if chunk.choices and (delta := chunk.choices[0].delta.content):  # Azure OpenAI can return empty chunks
            state.messages[-1]["content"] += delta
            await send(Span(delta, id=f"chat-content-{len(state.messages) - 1}", hx_swap_oob=swap))

    current_timestamp = next_timestamp

    last_user_message = state.last_user_prompt
    # feedback = await ask_tutor(state)
    # feedback_rendered = render_feedback(last_user_message, feedback, "tutor_content")
    # await send(feedback_rendered)

    # tmp disable it ...
    # feedback = await ask_history_tutor(state)
    # feedback_rendered = render_feedback(last_user_message, feedback, "tutor_history_content")
    # await send(feedback_rendered)

    # feedback = await feedback_on_all_messages(state)
    # feedback_rendered = render_feedback("last: " + last_user_message, feedback, ID_FEEDBACK_3, 'true')
    # await send(feedback_rendered)

    # feedback = await resume_feedback(state)
    # feedback_rendered = render_feedback("last: " + last_user_message, feedback, ID_FEEDBACK_4, 'true')
    # await send(feedback_rendered)
