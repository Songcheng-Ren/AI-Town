import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from api.websocket import chat_endpoint, npc_state_endpoint, ConnectionManager, turtle_endpoint
app = FastAPI()
manager = ConnectionManager()
from agent.utils.llm import LLMCaller
from agent.prompt.prompt import Prompt

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_turtle(websocket: WebSocket):
    await turtle_endpoint(websocket, manager)

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     caller = LLMCaller('custom')
#     while True:
#         data = await websocket.receive_text()
#         response = await caller.ask(data)
#         await websocket.send_text(f"Message text was: {response}")


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)