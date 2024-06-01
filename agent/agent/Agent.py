from sqlalchemy.orm import Session
from sql import crud, models, schemas
from sql.database import get_db, engine
from agent.prompt.prompt import Prompt
from typing import List, Dict, Any
from agent.utils.llm import LLMCaller
import datetime
from embedding.similarity import getTop, addData


class Agent:
    def __init__(self, player_id: int, db: Session):
        self.player_id = player_id
        self.player_sex = None
        self.future = None
        self.goal = None
        self.skill = None
        self.character = None
        self.background = None
        self.player_age = None
        self.player_name = None
        self.db = db
        self.load_information()
        self.prompts = {
            "plan": Prompt("plan"),
            "act": Prompt("act"),
            "critic": Prompt("critic"),
            "isDone": Prompt("isDone"),
            "reflectionDay": Prompt("reflectionDay")
        }
        self.caller = LLMCaller('gpt35')
        self.script = ""
        self.plan_memory = ""
        self.act_memory = ""


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
        db_game = crud.get_game(db=self.db, username=db_player.username)
        self.script = db_game.script

    def get_text(self, part: str, params: Dict[str, Any]) -> str:
        return self.prompts[part].to_string(params)

    async def plan(self):
        # 提取最近的10条记忆
        latest_memory = ""
        db_memory = crud.get_his_memory(db=self.db, player_id=self.player_id)
        db_memory.sort(key=lambda x: x.created_time, reverse=True)
        n = len(db_memory)
        if n <= 10:
            count = n
        else:
            count = 10
        for i in range(count):
            latest_memory = latest_memory + str(i + 1) + "." + db_memory[i].description + "\n"
        request = self.get_text("plan", {
            "{script}": self.script,
            "{player_name}": self.player_name,
            "{player_sex}": self.player_sex,
            "{player_age}": self.player_age,
            "{background}": self.background,
            "{character}": self.character,
            "{skill}": self.skill,
            "{goal}": self.goal,
            "{future}": self.future,
            "{latest_memory}": latest_memory
        })
        response = await self.caller.ask(request)
        print(response)
        temp = response.get("response", "")
        content = response.get("act", temp)
        self.plan_memory = content


    async def act(self):
        # 提取与计划有关的10条记忆
        related_memory = getTop(self.player_id, self.plan_memory, 10)
        request = self.get_text("act", {
            "{script}": self.script,
            "{player_name}": self.player_name,
            "{player_sex}": self.player_sex,
            "{player_age}": self.player_age,
            "{background}": self.background,
            "{character}": self.character,
            "{skill}": self.skill,
            "{goal}": self.goal,
            "{future}": self.future,
            "{plan}": self.plan_memory,
            "{related_memory}": related_memory,
            "{act}": self.act_memory
        })
        response = await self.caller.ask(request)
        print(response)
        temp = response.get("response", "")
        act = response.get("act", temp)
        crud.add_journal(db=self.db, journal_data=act, player_id=self.player_id, created_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        request =self.get_text("critic", {
            "{script}": self.script,
            "{player_name}": self.player_name,
            "{player_sex}": self.player_sex,
            "{player_age}": self.player_age,
            "{background}": self.background,
            "{character}": self.character,
            "{skill}": self.skill,
            "{goal}": self.goal,
            "{future}": self.future,
            "{plan}": self.plan_memory,
            "{related_memory}": related_memory,
            "{act}": self.act_memory,
            "{activity}": act
        })
        response = await self.caller.ask(request)
        print(response)
        temp = response.get("response", "")
        content = response.get("critic", temp)
        importance = response.get("importance", 5)
        index = addData(self.player_id, content)
        crud.add_memory(db=self.db, player_id=self.player_id, memory_type="knowledge", related_id=-1,
                        description=content, importance=importance,
                        created_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), embedding_id=index)
        self.act_memory = self.act_memory + "\n" + content
        return content

    async def isDone(self):
        related_memory = getTop(self.player_id, self.plan_memory, 10)
        request = self.get_text("isDone", {
            "{script}": self.script,
            "{player_name}": self.player_name,
            "{player_sex}": self.player_sex,
            "{player_age}": self.player_age,
            "{background}": self.background,
            "{character}": self.character,
            "{skill}": self.skill,
            "{goal}": self.goal,
            "{future}": self.future,
            "{plan}": self.plan_memory,
            "{related_memory}": related_memory,
            "{act}": self.act_memory
        })
        response = await self.caller.ask(request)
        judge = response.get("judge", 0)
        if judge:
            return True
        return False

    async def reflect(self):
        request = self.get_text("reflectionDay", {
            "{script}": self.script,
            "{player_name}": self.player_name,
            "{player_sex}": self.player_sex,
            "{player_age}": self.player_age,
            "{background}": self.background,
            "{character}": self.character,
            "{skill}": self.skill,
            "{goal}": self.goal,
            "{future}": self.future,
            "{act}": self.act_memory
        })
        response = await self.caller.ask(request)
        print(response)
        temp = response.get("response", "")
        content = response.get("summary", temp)
        importance = response.get("importance", 5)
        index = addData(self.player_id, content)
        crud.add_memory(db=self.db, player_id=self.player_id, memory_type="knowledge", related_id=-1,
                        description=content, importance=importance,
                        created_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), embedding_id=index)
