import uvicorn
from fastapi import Depends, FastAPI, HTTPException, WebSocket

from sqlalchemy.orm import Session

from agent.chat.ChatWithNPC import ChatWithNPC
from agent.utils.llm import LLMCaller
from sql import crud, models
from sql.schemas import StartAgents, StopAgents
from sql.database import get_db, engine
models.Base.metadata.create_all(bind=engine)

from api.websocket import chat_endpoint, npc_state_endpoint, ConnectionManager, turtle_endpoint, plot_endpoint
from api.login import router as login_router
from api.initGame import router as init_router
from api.updateData import router as update_router
from fastapi.middleware.cors import CORSMiddleware
from api.agent_manager import start_agents, stop_agents
app = FastAPI()

# 设置允许的来源
origins = [
    "http://localhost:3000",  # 允许前端服务的 URL
    "http://127.0.0.1:3000"
]

# 添加 CORS 中间件，允许预检请求（OPTIONS）以及其他设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许的域名列表
    allow_credentials=True,
    allow_methods=["*"],  # 允许的方法
    allow_headers=["*"],  # 允许的头部
)

app.include_router(login_router)
app.include_router(init_router)
app.include_router(update_router)
manager = ConnectionManager()


@app.post("/start_agents")
async def start(start: StartAgents, db: Session = Depends(get_db)):
    print(start.agents)
    await start_agents(start.agents, db)
    return {"message": "Agents are being started"}


@app.post("/stop_agents")
async def stop(stop: StopAgents):
    await stop_agents(stop.agents)
    return {"message": "Agents have been stopped"}


@app.websocket("/ws/chat/{player_id}/{other_id}")
async def websocket_chat(websocket: WebSocket, player_id: int, other_id: int, db: Session = Depends(get_db)):
    await chat_endpoint(websocket, manager, player_id, other_id, db)


@app.websocket("/ws/npc/{client_id}")
async def websocket_npc(websocket: WebSocket, client_id: int):
    await npc_state_endpoint(websocket, manager)


@app.websocket("/ws/turtle")
async def websocket_turtle(websocket: WebSocket):
    await turtle_endpoint(websocket, manager)


@app.websocket("/ws/plot/{username}")
async def websocket_plot(websocket: WebSocket, username: str, db: Session = Depends(get_db)):
    await plot_endpoint(websocket, manager, username, db)


@app.get("/")
async def root():
    caller = LLMCaller('gpt35')
    response = await caller.ask("What is your name?")
    print(response)
    return {"messeage": response}


@app.get("/{player_id}")
async def chat_with_npc(player_id: int, db: Session = Depends(get_db)):
    chat = ChatWithNPC(player_id=player_id, db=db)
    response = await chat.niceToMeetYou()
    return {"messeage": response}


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
