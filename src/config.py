from dataclasses import dataclass

_config = None

KEY_DESCRIPTION = {
    "scenario_name": "Chat with me",
    "description": "Description of scenario",
    "bot_name": "The name of the bot 'personage' (will only be used on the display)",
    "bot_first_msg": "The first message the bot says when we land on the page.",
    "role_prompt": "The system prompt used to 'tune' the bot",
    "role_temperature": "The temperature used by the 'role' bot",
    "role_model": "gpt4o, gpt4o-mini, ...",
    "feedback_1_prompt": "",
    "feedback_1_temperature": "",
    "feedback_1_use_history": "If 'true' then the feedbacks are one long conversation that has started by the system prompt then followed by the users prompt with only the assistant prompt displayed ",
    "feedback_1_model": "gpt4o, gpt4o-mini, ...",
    "feedback_2_prompt": "",
    "feedback_2_temperature": "",
    "feedback_2_use_history": "If 'true' then the feedbacks are one long conversation that has started by the system prompt then followed by the users prompt with only the assistant prompt displayed ",
    "feedback_2_model": "gpt4o, gpt4o-mini, ...",
    "resume_1_prompt": "",
    "resume_1_temperature": "",
    "resume_1_use_feedbacks": "If 'true' then all feedback will be provided, other wise, all conversation is provided",
    "resume_1_model": "gpt4o, gpt4o-mini, ...",
    "resume_2_prompt": "",
    "resume_2_temperature": "",
    "resume_2_use_feedbacks": "If 'true' then all feedback will be provided, other wise, all conversation is provided",
    "resume_2_model": "gpt4o, gpt4o-mini, ...",
}


def get_config(force_update=False):
    global _config
    if _config is None or force_update:
        _config = Config()
    return _config


class Config:
    def __init__(self):
        self.dict = {}
        # fill it


@dataclass
class ConfigEntry:
    scenario_id: int
    key: str
    content: str
    # last_modification ?
