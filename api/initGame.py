from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sql.database import get_db
from sql.schemas import GetScript, ChangeScript, GetSetting, ChangeSetting
from sql import crud
from agent.utils.llm import LLMCaller
from agent.prompt.prompt import Prompt
import json
from .dependencies import get_current_user
router = APIRouter()

# 请求：用户名
@router.post("/get_script")
async def get_script(script: GetScript, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    if script.username != current_user:
        raise HTTPException(status_code=403, detail="Unauthorized to access this script")
    db_script = crud.get_game(db, username=script.username)
    if not db_script:
        raise HTTPException(status_code=404, detail="Script not found for the user")
    return {"script": db_script.script}


# 请求：用户名和要求
@router.post("/change_script")
async def change_script(script: ChangeScript, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    if script.username != current_user:
        raise HTTPException(status_code=403, detail="Unauthorized to access this script")
    caller = LLMCaller('gpt35')
    prompt = Prompt("changeScript")
    request = prompt.to_string({
        "{requirement}": script.requirement,
    })
    response = await caller.ask(request)
    print(response)
    try:
        crud.change_script(db, script.username, response["response"])
    except:
        raise HTTPException(status_code=400, detail="Change failed!")
    return {"script": response["response"]}


# 请求：用户名和角色号
@router.post("/get_setting")
async def get_setting(setting: GetSetting, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    if setting.username != current_user:
        raise HTTPException(status_code=403, detail="Unauthorized to access this script")
    db_player = crud.get_player(db, player_id=setting.player_id)
    if db_player is None:
        raise HTTPException(status_code=404, detail="player not found")
    return {"player_id": db_player.player_id,
            "player_name": db_player.player_name,
            "player_age": db_player.player_age,
            "background": db_player.background,
            "character": db_player.character,
            "skill": db_player.skill,
            "goal": db_player.goal,
            "future": db_player.future,
            "player_sex": db_player.player_sex
            }


# 请求：用户名、角色号、要求
@router.post("/change_setting")
async def change_setting(setting: ChangeSetting, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    if setting.username != current_user:
        raise HTTPException(status_code=403, detail="Unauthorized to access this script")
    caller = LLMCaller('gpt35')
    prompt = Prompt("changeSetting")
    db_game = crud.get_game(db, username=setting.username)
    request = prompt.to_string({
        "{script}": db_game.script,
        "{requirement}": setting.requirement
    })
    response = await caller.ask(request)
    print(response)
    default_setting = crud.get_all_npc(db, username="0")
    player_name = response.get("player_name", default_setting[1].player_name)
    player_sex = response.get("player_sex", default_setting[1].player_sex)
    player_age = response.get("player_age", default_setting[1].player_age)
    background = response.get("background", default_setting[1].background)
    character = response.get("character", default_setting[1].character)
    skill = response.get("skill", default_setting[1].skill)
    goal = response.get("goal", default_setting[1].goal)
    future = response.get("future", default_setting[1].future)
    db_player = crud.change_player(db, player_id=setting.player_id, player_name=player_name, player_age=player_age,
                                       background=background, character=character, skill=skill, goal=goal, future=future,
                                       player_sex=player_sex)
    if not db_player:
        raise HTTPException(status_code=400, detail="Change failed!")
    return {"player_name": player_name,
            "player_age": player_age,
            "background": background,
            "character": character,
            "skill": skill,
            "goal": goal,
            "future": future,
            "player_sex": player_sex
            }


