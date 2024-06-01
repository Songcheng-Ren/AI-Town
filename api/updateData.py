from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sql.database import get_db
from sql.schemas import UpdateData
from sql import crud
from .dependencies import get_current_user
router = APIRouter()


# 请求：用户名, npcIds
@router.post("/update_npc_state")
async def update_npc_state(user: UpdateData, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    if user.username != current_user:
        raise HTTPException(status_code=403, detail="Unauthorized to access this script")
        # 解析npcIds
    npc_ids = user.npcIds.split(',')
    # 准备数据容器
    npc_data = []

    # 处理每个NPC ID
    for npc_id in npc_ids:
        npc_info = crud.get_player(db, player_id=npc_id)
        if not npc_info:
            continue  # 如果没有找到NPC信息，跳过

        # 获取此NPC的所有日志，限制为最多50条
        journal_entries = crud.get_journals(db, player_id=npc_id)

        # 构建响应数据
        journals = [{
            'journal_data': entry.journal_data,
            'created_time': entry.created_time  # 格式化时间
        } for entry in journal_entries]  # 列表推导收集所有日志条目

        # 如果有日志信息，添加到返回数据
        if journals:
            npc_data.append({
                'npc_id': npc_id,
                'npc_name': npc_info.player_name,
                'journals': journals  # 添加一个列表，包含所有相关的日志
            })
    print(npc_data)
    return npc_data

