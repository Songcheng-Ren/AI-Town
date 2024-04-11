from typing import List, Union

from pydantic import BaseModel


class Player(BaseModel):
    player_id: int
    player_name: str

    class Config:
        orm_mode = True