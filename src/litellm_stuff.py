from typing import Any
import yaml
from litellm import acompletion
from functools import cache

from config import get_scenario_config

class Models:
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.reload()

    def reload(self) -> None:
        with open(self.filename, "r") as file:
            config = yaml.safe_load(file)
            model_list = config["model-list"]
            self.model_dict = { model["model_name"] : model["litellm_params"] for model in model_list }

    def list(self) -> list[str]:
        return list(self.model_dict.keys())
    
    def params(self, model_name: str) -> dict[str, Any]:
        return self.model_dict[model_name]

models = Models("src/litellm-config.yaml")

async def complete(model: str, system_prompt: str, messages: dict[str, str], temperature: float, stream=False):
    messages_to_send = [{"role": "system", "content": system_prompt}] + messages
    stream = await acompletion(
        messages=messages_to_send,
        temperature=float(temperature),
        stream=stream,
        **models.params(model)
    )
    return stream

if __name__ == "__main__":
    from pprint import pprint
    pprint(models.model_dict)