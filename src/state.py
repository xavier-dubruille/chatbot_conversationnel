import uuid
from dataclasses import dataclass

_states = {}


@dataclass
class State:
    messages: []
    tutor_feedbacks: []
    scenario_id: int = 1

    @property
    def last_user_prompt(self):
        return next(
            (message["content"] for message in reversed(self.messages) if message["role"] == "user"),
            None
        )


def get_state(session) -> State:
    if 'session_id' not in session or session['session_id'] not in _states:
        session['session_id'] = str(uuid.uuid4())
        _states[session['session_id']] = State(messages=[], tutor_feedbacks=[])

    return _states.get(session['session_id'])
