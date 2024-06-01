from typing import List, Union

from pydantic import BaseModel


class Player(BaseModel):
    player_id: int
    player_name: str

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    username: str
    password: str  # 用户提交的原始密码（将在服务器端进行加密处理）


class GetScript(BaseModel):
    username: str


class ChangeScript(BaseModel):
    username: str
    requirement: str


class GetSetting(BaseModel):
    username: str
    player_id: int


class ChangeSetting(BaseModel):
    username: str
    player_id: int
    requirement: str


class StartAgents(BaseModel):
    agents: str


class StopAgents(BaseModel):
    agents: str


class UpdateData(BaseModel):
    username: str
    npcIds: str