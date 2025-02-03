import uuid
from dataclasses import dataclass

# from config import Config

_states = {}


@dataclass
class State:
    messages: []
    tutor_feedbacks: []
    # _config: Config = None
    scenario_id: int = 1
    assistant_finished_timestamp = 0.0
    assistant_started_timestamp = 0.0

    @property
    def last_user_prompt(self):
        return next(
            (message["content"] for message in reversed(self.messages) if message["role"] == "user"),
            None
        )

    @property
    def last_assistant_prompt(self):
        return next(
            (message["content"] for message in reversed(self.messages) if message["role"] == "assistant"),
            None
        )

    # @property
    # def config(self):
    #     return self.get_config(force_update=False)
    #
    # def get_config(self, force_update=False):
    #     if force_update or not self._config or self._config.scenario_id != self.scenario_id:
    #         self._config = Config(self.scenario_id)
    #     return self._config


def get_state(session) -> State:
    if 'session_id' not in session or session['session_id'] not in _states:
        session['session_id'] = str(uuid.uuid4())
        _states[session['session_id']] = State(messages=[], tutor_feedbacks=[])

    return _states.get(session['session_id'])
