from typing import List

import uvicorn
from fastapi import Depends, FastAPI, HTTPException

from sqlalchemy.orm import Session

from agent.chat.ChatWithNPC import ChatWithNPC
from agent.utils.llm import LLMCaller
from sql import crud, models, schemas
from sql.database import get_db, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
async def root():
    caller = LLMCaller('custom')
    response = await caller.ask("What is your name?")
    print(response)
    return {"messeage": response}
@app.get("/{player_id}")
async def chat_with_npc(player_id: int, db: Session = Depends(get_db)):
    chat = ChatWithNPC(player_id=player_id, db=db)
    response = await chat.niceToMeetYou()
    return {"messeage": response}


@app.get("/players/{player_id}", response_model=schemas.Player)
def read_user(player_id: int, db: Session = Depends(get_db)):
    db_player = crud.get_player(db, player_id=player_id)
    print(db_player.player_id)
    if db_player is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_player


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)