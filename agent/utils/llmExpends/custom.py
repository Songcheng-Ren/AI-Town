from typing import List, Dict, Any
import os
import json
import httpx
from agent.utils.llmExpends.BasicCaller import BasicCaller


class CustomCaller(BasicCaller):
    async def ask(self, prompt: str) -> str:
        counter = 0
        result = "{}"
        function_app_host = "chat20231211153137.chinacloudsites.cn"
        url_chat = f"https://{function_app_host}/api/FunctionChat"
        function_key = "MgKyDnbCnoWNINPGhUKktvNz2pyMgHJIheSbREWzQqjCAzFuMhDsLw=="
        function_url = f"{url_chat}?code={function_key}"
        while counter < 3:
            try:
                response_body = {
                    "Options": None,
                    "Messages": [{"Role": "User", "Content": prompt}],
                    "Temperature": 0.7,
                    "Max_tokens": 800,
                    "Nucleus_sampling_factor": 0.95,
                    "Frequency_penalty": 0,
                    "Presence_penalty": 0
                }
                headers = {"Content-Type": "application/json"}
                json_data = json.dumps(response_body)
                async with httpx.AsyncClient() as client:
                    response = await client.post(function_url, data=json_data, headers=headers)
                    result = response.json()["Choices"][0]["Message"]["Content"]
                    break
            except Exception as e:
                print(e)
                counter += 1
        return result