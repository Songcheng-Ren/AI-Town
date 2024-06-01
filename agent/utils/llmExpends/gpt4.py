from typing import List, Dict, Any
import os
import json
import openai_async as openai
from agent.utils.llmExpends.BasicCaller import BasicCaller
os.environ["http_proxy"] = "http://localhost:7890"
os.environ["https_proxy"] = "http://localhost:7890"

abs_path = os.path.dirname(os.path.realpath(__file__))

your_key = "sk-proj-kn9VxK9ETGMZK2hZte31T3BlbkFJZj9naeMnTpj9Gmd805XT"

class GPT4Caller(BasicCaller):
    def __init__(self) -> None:
        self.model = "gpt-4-turbo"
        self.api_key = your_key

    async def ask(self, prompt: str) -> str:
        counter = 0
        result = "{}"
        while counter < 3:
            try:
                request_body = {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    'temperature': 0
                }
                response = await openai.chat_complete(self.api_key, 50, request_body)
                result = response.json()["choices"][0]["message"]["content"]
                return result
            except Exception as e:
                print(e)
                counter += 1
        return result