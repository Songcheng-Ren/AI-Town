from typing import List

import uvicorn
from fastapi import Depends, FastAPI, HTTPException

from sqlalchemy.orm import Session

from agent.utils.llm import LLMCaller
from sql import crud, models, schemas
from sql.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# @app.get("/")
# async def root():
#     caller = LLMCaller('custom')
#     response = await caller.ask("What is your name?")
#     return {"message": response}

@app.get("/players/{player_id}", response_model=schemas.Player)
def read_user(player_id: int, db: Session = Depends(get_db)):
    db_player = crud.get_player(db, player_id=player_id)
    print(db_player.player_id)
    if db_player is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_player


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)