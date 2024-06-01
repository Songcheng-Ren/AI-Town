# websocket.py
from fastapi import WebSocket
from typing import List
from agent.utils.llm import LLMCaller
from agent.prompt.prompt import Prompt
import json
from agent.chat.ChatWithNPC import ChatWithNPC
from sqlalchemy.orm import Session
from sql import crud, models, schemas

class ConnectionManager:
    def __init__(self):
        self.chat_connections: List[WebSocket] = []
        self.npc_state_connections: List[WebSocket] = []
        self.turtle_connections: List[WebSocket] = []
        self.plot_connections: List[WebSocket] = []

    async def connect_chat(self, websocket: WebSocket):
        await websocket.accept()
        self.chat_connections.append(websocket)

    async def connect_npc_state(self, websocket: WebSocket):
        await websocket.accept()
        self.npc_state_connections.append(websocket)

    async def connect_turtle(self, websocket: WebSocket):
        await websocket.accept()
        self.turtle_connections.append(websocket)

    async def connect_plot(self, websocket: WebSocket):
        await websocket.accept()
        self.plot_connections.append(websocket)

    def disconnect_chat(self, websocket: WebSocket):
        self.chat_connections.remove(websocket)

    def disconnect_npc_state(self, websocket: WebSocket):
        self.npc_state_connections.remove(websocket)

    def disconnect_turtle(self, websocket: WebSocket):
        self.turtle_connections.remove(websocket)

    def disconnect_plot(self, websocket: WebSocket):
        self.plot_connections.remove(websocket)

    async def broadcast_chat(self, message: str):
        for connection in self.chat_connections:
            await connection.send_text(message)

    async def broadcast_npc_state(self, message: str):
        for connection in self.npc_state_connections:
            await connection.send_text(message)


async def chat_endpoint(websocket: WebSocket, manager: ConnectionManager, player_id: int, other_id: int, db: Session):
    await manager.connect_chat(websocket)
    try:
        chat_npc = ChatWithNPC(player_id=player_id, other_id=other_id, db=db)
        if crud.is_first_communication(db, player_id=player_id, other_id=other_id):
            content = await chat_npc.startConversation()
        else:
            content = await chat_npc.niceToMeetYou()
        await websocket.send_text(json.dumps({
            "type": "npcMessage",
            "content": content
        }))
        while True:
            data = await websocket.receive_text()
            data_json = json.loads(data)  # 解析 JSON 数据
            question = data_json['content']  # 前端发送的消息内容
            content = await chat_npc.converse(question)
            await websocket.send_text(json.dumps({
                "type": "npcMessage",
                "content": content
            }))
            result = await chat_npc.walkAway()
            if result[0]:
                await websocket.send_text(json.dumps({
                    "type": "npcMessage",
                    "content": result[1]
                }))
                await websocket.send_text(json.dumps({
                    "type": "end"
                }))
                await chat_npc.reflectionChat()
                break
    #except Exception as e:
    #  print(f'Error: {e}')
    finally:
        manager.disconnect_chat(websocket)

async def npc_state_endpoint(websocket: WebSocket, manager: ConnectionManager):
    await manager.connect_npc_state(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast_npc_state(f"NPC update: {data}")
    except Exception as e:
        print(f'Error: {e}')
    finally:
        manager.disconnect_npc_state(websocket)


async def turtle_endpoint(websocket: WebSocket, manager: ConnectionManager):
    await manager.connect_turtle(websocket)
    try:
        history = ""
        caller = LLMCaller('gpt4')
        prompt1 = Prompt("turtle")
        prompt2 = Prompt("basic")
        request = prompt1.to_string({})
        history = history + "用户说：" + request + "\n"
        response = await caller.ask(request)
        content = response['response']
        history = history + content + "\n"
        await websocket.send_text(json.dumps({
            "type": "npcMessage",
            "content": content
        }))
        while True:
            data = await websocket.receive_text()
            data_json = json.loads(data)  # 解析 JSON 数据
            question = data_json['content']  # 前端发送的消息内容
            request = prompt2.to_string({"{history}": history,
                                         "{question}": question
                                         })
            history = history + "用户说：" + data + "\n"
            response = await caller.ask(request)
            content = response['response']
            history = history + content + "\n"
            await websocket.send_text(json.dumps({
                "type": "npcMessage",
                "content": content
            }))
    except Exception as e:
        print(f'Error: {e}')
    finally:
        manager.disconnect_turtle(websocket)


async def plot_endpoint(websocket: WebSocket, manager: ConnectionManager, username: str, db: Session):
    await manager.connect_plot(websocket)
    try:
        game = crud.get_game(db=db, username=username)
        script = game.script
        history = ""
        caller = LLMCaller('gpt4')
        prompt1 = Prompt("plot")
        prompt2 = Prompt("basic")
        request = prompt1.to_string({"script": script})
        history = history + "用户说：" + request + "\n"
        response = await caller.ask(request)
        print(response)
        content = response['response']
        history = history + content + "\n"
        await websocket.send_text(json.dumps({
            "type": "npcMessage",
            "content": content
        }))
        while True:
            data = await websocket.receive_text()
            data_json = json.loads(data)  # 解析 JSON 数据
            question = data_json['content']  # 前端发送的消息内容
            request = prompt2.to_string({"{history}": history,
                                         "{question}": question
                                         })
            history = history + "用户说：" + data + "\n"
            response = await caller.ask(request)
            print(response)
            content = response['response']
            history = history + content + "\n"
            await websocket.send_text(json.dumps({
                "type": "npcMessage",
                "content": content
            }))
    except Exception as e:
        print(f'Error: {e}')
    finally:
        manager.disconnect_plot(websocket)
