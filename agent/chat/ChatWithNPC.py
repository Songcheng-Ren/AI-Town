from sqlalchemy.orm import Session
from sql import crud, models, schemas
from sql.database import get_db, engine
from agent.prompt.prompt import Prompt
from typing import List, Dict, Any
from agent.utils.llm import LLMCaller


class ChatWithNPC:
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
            "niceToMeetYou": Prompt("niceToMeetYou")
        }
        self.caller = LLMCaller('custom')

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

    def get_text(self, part: str, params: Dict[str, Any]) -> str:
        return self.prompts[part].to_string(params)
    async def niceToMeetYou(self):
        request = self.get_text("niceToMeetYou", {
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
        return response

    async def startConversation(self):
        pass

    async def converse(self):
        pass
    async def walkAway(self):
        pass



