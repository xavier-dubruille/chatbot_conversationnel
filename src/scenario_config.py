from dataclasses import dataclass, field, fields
from typing import Optional

MAIN_CAT = "main"
ROLE_CAT = "role"
FEEDBACK1_CAT = "feedback1"
FEEDBACK2_CAT = "feedback2"
RESUME1_CAT = "resume1"
RESUME2_CAT = "resume2"


@dataclass
class ScenarioConfig:
    id: int = field(default=0, metadata={
        "description": "the unique id of the scenario",
        "category": MAIN_CAT}),
    scenario_name: str = field(default="", metadata={
        "description": "The name, the title, used for this scenario",
        "category": MAIN_CAT})
    description: str = field(default="", metadata={
        "description": "Description of this scenario (only meant to help you.  It's not used anywhere else)",
        "category": MAIN_CAT})
    bot_name: str = field(default="", metadata={
        "description": "The name of the bot 'personage' (will only be used on the display)",
        "category": ROLE_CAT})
    bot_first_msg: str = field(default="", metadata={
        "description": "The first message the bot says when we land on the page.",
        "category": ROLE_CAT})
    role_prompt: str = field(default="", metadata={
        "description": "The system prompt used to 'tune' the bot",
        "category": ROLE_CAT})
    role_temperature: Optional[float] = field(default=None, metadata={
        "description": "The temperature used by the 'role' bot",
        "category": ROLE_CAT})
    role_model: str = field(default="", metadata={
        "description": "gpt4o, gpt4o-mini, ...",
        "category": ROLE_CAT})
    feedback_1_prompt: str = field(default="", metadata={
        "description": "",
        "category": FEEDBACK1_CAT})
    feedback_1_temperature: Optional[float] = field(default=None, metadata={
        "description": "",
        "category": FEEDBACK1_CAT})
    feedback_1_use_history: bool = field(default=False, metadata={
        "description": "If 'true' then the feedbacks are one long conversation that has started by the system prompt then followed by the users prompt with only the assistant prompt displayed",
        "category": FEEDBACK1_CAT})
    feedback_1_model: str = field(default="", metadata={
        "description": "gpt4o, gpt4o-mini, ...",
        "category": FEEDBACK1_CAT})
    feedback_2_prompt: str = field(default="", metadata={
        "description": "",
        "category": FEEDBACK2_CAT})
    feedback_2_temperature: Optional[float] = field(default=None, metadata={
        "description": "",
        "category": FEEDBACK2_CAT})
    feedback_2_use_history: bool = field(default=False, metadata={
        "description": "If 'true' then the feedbacks are one long conversation that has started by the system prompt then followed by the users prompt with only the assistant prompt displayed",
        "category": FEEDBACK2_CAT})
    feedback_2_model: str = field(default="", metadata={
        "description": "gpt4o, gpt4o-mini, ...",
        "category": FEEDBACK2_CAT})
    resume_1_prompt: str = field(default="", metadata={
        "description": "",
        "category": RESUME1_CAT})
    resume_1_temperature: Optional[float] = field(default=None, metadata={
        "description": "",
        "category": RESUME1_CAT})
    resume_1_use_feedbacks: bool = field(default=False, metadata={
        "description": "If 'true' then all feedback will be provided, other wise, all conversation is provided",
        "category": RESUME1_CAT})
    resume_1_model: str = field(default="", metadata={
        "description": "gpt4o, gpt4o-mini, ...",
        "category": RESUME1_CAT})
    resume_2_prompt: str = field(default="", metadata={
        "description": "",
        "category": RESUME2_CAT})
    resume_2_temperature: Optional[float] = field(default=None, metadata={
        "description": "",
        "category": RESUME2_CAT})
    resume_2_use_feedbacks: bool = field(default=False, metadata={
        "description": "If 'true' then all feedback will be provided, other wise, all conversation is provided",
        "category": RESUME2_CAT})
    resume_2_model: str = field(default="", metadata={
        "description": "gpt4o, gpt4o-mini, ...",
        "category": RESUME2_CAT})


def get_attribute_descriptions(category_name="all"):
    """Retourne une liste des paires attribut-description de la dataclass."""
    attribute_descriptions = []
    for fi in fields(ScenarioConfig):
        description = fi.metadata.get("description", "No description provided")
        category = fi.metadata.get("category", "main")
        if category_name == "all" or category == category_name:
            attribute_descriptions.append((fi.name, description))
    return attribute_descriptions


def create_exemple_scenario_config():
    return ScenarioConfig(
        id=0,
        scenario_name="Chat with Assistant",
        description="A scenario where the user chats with a helpful assistant bot.",
        bot_name="HelperBot",
        bot_first_msg="Hello! How can I assist you today?",
        role_prompt="You are a helpful assistant designed to provide accurate and concise information.",
        role_temperature=0.7,
        role_model="gpt4o",
        feedback_1_prompt="What improvements can be made based on the user's response?",
        feedback_1_temperature=0.5,
        feedback_1_use_history=True,
        feedback_1_model="gpt4o-mini",
        feedback_2_prompt="Analyze the conversation flow for clarity.",
        feedback_2_temperature=0.6,
        feedback_2_use_history=False,
        feedback_2_model="gpt4o",
        resume_1_prompt="Summarize the key points of the conversation.",
        resume_1_temperature=0.4,
        resume_1_use_feedbacks=True,
        resume_1_model="gpt4o-mini",
        resume_2_prompt="Provide a concise summary highlighting important feedback.",
        resume_2_temperature=0.5,
        resume_2_use_feedbacks=False,
        resume_2_model="gpt4o"
    )
