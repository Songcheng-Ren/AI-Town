from typing import List, Dict, Any
import json
import re

from agent.utils.llmExpends.BasicCaller import BasicCaller
from agent.utils.llmExpends.custom import CustomCaller

# TODO: make the LLMCaller more general
choices = {
    'custom': CustomCaller,
}


def get_caller(model: str) -> BasicCaller:
    return choices[model]


class LLMCaller:
    def __init__(self, model: str) -> None:
        self.model = model
        self.caller = get_caller(model)()

    async def ask(self, prompt: str) -> Dict[str, Any]:
        result = await self.caller.ask(prompt)
        try:
            result = json.loads(result)
        except Exception:
            try:
                info = re.findall(r"\{.*\}", result, re.DOTALL)
                if info:
                    info = info[-1]
                    result = json.loads(info)
                else:
                    result = {"response": result}
            except Exception:
                result = {"response": result}
        return result
