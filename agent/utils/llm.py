from typing import List, Dict, Any
import json
import re

from agent.utils.llmExpends.BasicCaller import BasicCaller
from agent.utils.llmExpends.custom import CustomCaller
from agent.utils.llmExpends.gpt35 import GPT35Caller
from agent.utils.llmExpends.gpt4 import GPT4Caller

# TODO: make the LLMCaller more general
choices = {
    'custom': CustomCaller,
    'gpt35': GPT35Caller,
    'gpt4': GPT4Caller
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
            # 如果返回字符串是json，直接转化为字典
            result = json.loads(result)
        except Exception:
            try:
                # 如果不是json，使用正则表达式试图获取json并转化为字典
                info = re.findall(r"\{.*\}", result, re.DOTALL)
                if info:
                    info = info[-1]
                    result = json.loads(info)
                else:
                    # 如果还失败，将返回内容封装在一个字典中，键值为response
                    result = {"response": result}
            except Exception:
                # 无论如何都返回一个字典
                result = {"response": result}
        return result
