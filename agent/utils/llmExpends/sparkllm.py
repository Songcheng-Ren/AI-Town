from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage

#星火认知大模型v3.5的URL值，其他版本大模型URL值请前往文档（https://www.xfyun.cn/doc/spark/Web.html）查看
SPARKAI_URL = 'wss://spark-api.xf-yun.com/v3.5/chat'
#星火认知大模型调用秘钥信息，请前往讯飞开放平台控制台（https://console.xfyun.cn/services/bm35）查看
SPARKAI_APP_ID = 'cb18c039'
SPARKAI_API_SECRET = 'MjkzOTRkZDRiYzdiZjcxNDk1ODM2OWFj'
SPARKAI_API_KEY = 'bd28d71d4bd415bd583a78e2d77e9bb1'
#星火认知大模型v3.5的domain值，其他版本大模型domain值请前往文档（https://www.xfyun.cn/doc/spark/Web.html）查看
SPARKAI_DOMAIN = 'generalv3.5'
from typing import List, Dict, Any
import os
import json
import httpx
from agent.utils.llmExpends.BasicCaller import BasicCaller


class SparkCaller(BasicCaller):
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


if __name__ == '__main__':
    spark = ChatSparkLLM(
        spark_api_url=SPARKAI_URL,
        spark_app_id=SPARKAI_APP_ID,
        spark_api_key=SPARKAI_API_KEY,
        spark_api_secret=SPARKAI_API_SECRET,
        spark_llm_domain=SPARKAI_DOMAIN,
        streaming=False,
    )
    messages = [ChatMessage(
        role="user",
        content='你好呀'
    )]
    handler = ChunkPrintHandler()
    a = spark.generate([messages], callbacks=[handler])
    print(a)