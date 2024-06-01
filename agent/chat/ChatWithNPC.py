from sqlalchemy.orm import Session
from sql import crud, models, schemas
from sql.database import get_db, engine
from agent.prompt.prompt import Prompt
from typing import List, Dict, Any
from agent.utils.llm import LLMCaller
import datetime
from embedding.similarity import addData, getTop
import random


class ChatWithNPC:
    def __init__(self, player_id: int, other_id: int, db: Session):
        self.player_id = player_id
        self.other_id = other_id
        self.player_sex = None
        self.future = None
        self.goal = None
        self.skill = None
        self.character = None
        self.background = None
        self.player_age = None
        self.player_name = None
        self.know = ""
        self.db = db
        self.load_information()
        self.prompts = {
            "niceToMeetYou": Prompt("niceToMeetYou"),
            "startConversation": Prompt("startConversation"),
            "converse": Prompt("converse"),
            "walkAway": Prompt("walkAway"),
            "reflectionChat": Prompt("reflectionChat")
        }
        self.caller = LLMCaller('gpt35')
        # 格式化时间
        self.created_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history = []
        self.script = ""

    def load_information(self) -> None:
        db_player = crud.get_player(db=self.db, player_id=self.player_id)
        if db_player:
            self.player_name = db_player.player_name
            self.player_age = db_player.player_age
            self.background = db_player.background
            self.character = db_player.character
            self.skill = db_player.skill
            self.goal = db_player.goal
            self.future = db_player.future
            self.player_sex = db_player.player_sex
        username = db_player.username
        db_game = crud.get_game(db=self.db, username=username)
        self.script = db_game.script
        db_know = crud.get_memory2other(db=self.db, player_id=self.player_id, other_id=self.other_id)
        if db_know:
            n = len(db_know)
            for i in range(n):
                num = i + 1
                self.know = self.know + str(num) + "." + db_know[i].description + "\n"


    def get_text(self, part: str, params: Dict[str, Any]) -> str:
        return self.prompts[part].to_string(params)


    async def niceToMeetYou(self) -> str:
        request = self.get_text("niceToMeetYou", {
            "{script}": self.script,
            "{player_name}": self.player_name,
            "{player_sex}": self.player_sex,
            "{player_age}": self.player_age,
            "{background}": self.background,
            "{character}": self.character,
            "{skill}": self.skill,
            "{goal}": self.goal,
            "{future}": self.future
        })
        response = await self.caller.ask(request)
        print(response)
        temp = response.get("response", "你好！")
        content = response.get("content", temp)
        importance = response.get("importance", 5)
        self.history.append([0, content, importance])
        return content


    async def startConversation(self) -> str:
        request = self.get_text("startConversation", {
            "{script}": self.script,
            "{player_name}": self.player_name,
            "{player_sex}": self.player_sex,
            "{player_age}": self.player_age,
            "{background}": self.background,
            "{character}": self.character,
            "{skill}": self.skill,
            "{goal}": self.goal,
            "{future}": self.future,
            "{know}": self.know
        })
        response = await self.caller.ask(request)
        print(response)
        temp = response.get("response", "你好！")
        content = response.get("content", temp)
        importance = response.get("importance", 5)
        self.history.append([0, content, importance])
        return content

    async def converse(self, question: str) -> str:
        conversation = ""
        related_memory = ""
        latest_memory = ""
        important_memory = ""
        random_memory = ""
        for h in self.history:
            if h[0]:
                conversation = conversation + "对方说：" + h[1] + "\n"
            else:
                conversation = conversation + "你说：" + h[1] + "\n"
        db_memory = crud.get_his_memory(db=self.db, player_id=self.player_id)
        # 提取随机5条记忆
        n = len(db_memory)
        if n <= 5:
            for i in range(n):
                random_memory = random_memory + str(i + 1) + "." + db_memory[i].description + "\n"
        else:
            random_numbers = [random.randint(0, n - 1) for _ in range(5)]
            for i in range(5):
                random_memory = random_memory + str(i + 1) + "." + db_memory[random_numbers[i]].description + "\n"
        # 提取最重要的5条记忆
        db_memory.sort(key=lambda x: x.importance, reverse=True)
        if n <= 5:
            count = n
        else:
            count = 5
        for i in range(count):
            important_memory = important_memory + str(i + 1) + "." + db_memory[i].description + "\n"
        # 提取最近5条记忆
        db_memory.sort(key=lambda x: x.created_time, reverse=True)
        for i in range(count):
            latest_memory = latest_memory + str(i + 1) + "." + db_memory[i].description + "\n"
        # 提取最相关的5条记忆
        related_memory = getTop(self.player_id, question, 5)
        request = self.get_text("converse", {
            "{script}": self.script,
            "{player_name}": self.player_name,
            "{player_sex}": self.player_sex,
            "{player_age}": self.player_age,
            "{background}": self.background,
            "{character}": self.character,
            "{skill}": self.skill,
            "{goal}": self.goal,
            "{future}": self.future,
            "{question}": question,
            "{conversation}": conversation,
            "{related_memory}": related_memory,
            "{latest_memory}": latest_memory,
            "{important_memory}": important_memory,
            "{random_memory}": random_memory,
            "{know}": self.know
        })
        response = await self.caller.ask(request)
        print(response)
        temp = response.get("response", "你好！")
        content = response.get("content", temp)
        importance = response.get("importance", 5)
        self.history.append([1, content, 0])
        self.history.append([0, content, importance])
        return content

    async def walkAway(self):
        conversation = ""
        for h in self.history:
            if h[0]:
                conversation = conversation + "对方说：" + h[1] + "\n"
            else:
                conversation = conversation + "你说：" + h[1] + "\n"
        request = self.get_text("walkAway", {
            "{script}": self.script,
            "{player_name}": self.player_name,
            "{player_sex}": self.player_sex,
            "{player_age}": self.player_age,
            "{background}": self.background,
            "{character}": self.character,
            "{skill}": self.skill,
            "{goal}": self.goal,
            "{future}": self.future,
            "{conversation}": conversation
        })
        response = await self.caller.ask(request)
        print(response)
        temp = response.get("response", "你好！")
        content = response.get("content", temp)
        judge = response.get("judge", 0)
        importance = response.get("importance", 5)
        self.history.append([0, content, importance])
        if judge:
            return [True, content]
        return [False, content]


    async def reflectionChat(self):
        conversation = ""
        for h in self.history:
            if h[0]:
                conversation = conversation + "对方说：" + h[1] + "\n"
            else:
                conversation = conversation + "你说：" + h[1] + "\n"
        request = self.get_text("reflectionChat", {
            "{script}": self.script,
            "{player_name}": self.player_name,
            "{player_sex}": self.player_sex,
            "{player_age}": self.player_age,
            "{background}": self.background,
            "{character}": self.character,
            "{skill}": self.skill,
            "{goal}": self.goal,
            "{future}": self.future,
            "{conversation}": conversation
        })
        response = await self.caller.ask(request)
        print(response)
        content1 = response.get("know", "")
        importance1 = response.get("importance1", 5)
        content2 = response.get("summary", "");
        importance2 = response.get("importance2", 5)
        index1 = addData(self.player_id, content1)
        crud.add_memory(db=self.db, player_id=self.player_id, memory_type="relationship", related_id=self.other_id, description=content1,
                        importance=importance1, created_time=self.created_time, embedding_id=index1)
        index2 = addData(self.player_id, content2)
        crud.add_memory(db=self.db, player_id=self.player_id, memory_type="knowledge", related_id=-1, description=content2, importance=importance2,
                        created_time=self.created_time, embedding_id=index2)
        journal_data = "与玩家进行对话"
        crud.add_journal(db=self.db, journal_data=journal_data, player_id=self.player_id, created_time=self.created_time)
