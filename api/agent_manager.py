import asyncio
from fastapi import HTTPException
from agent.agent.Agent import Agent


agents = {}  # 存储活跃的Agent实例
agent_tasks = {}  # 存储Agent的asyncio.Task对象


async def manage_agent(agent_id: int, db):
    agent = Agent(player_id=agent_id, db=db)
    agents[agent_id] = agent  # 存储Agent实例

    # 开始Agent的工作周期
    await agent.plan()
    try:
        while True:
            await asyncio.sleep(60)
            await agent.act()
            await asyncio.sleep(60)
            done = await agent.isDone()
            if done:
                await agent.reflect()
                await asyncio.sleep(1440)  # 等待100秒后再次开始plan
                await agent.plan()
            else:
                continue  # 如果未完成，则10秒后继续act
    except asyncio.CancelledError:
        print(f"Agent {agent_id}'s task was cancelled.")
    finally:
        # 清理工作
        agents.pop(agent_id, None)
        agent_tasks.pop(agent_id, None)


async def start_agents(agent_ids: str, db):
    ids = agent_ids.split(',')
    for agent_id in ids:
        int_id = int(agent_id)
        if int_id not in agents:
            task = asyncio.create_task(manage_agent(int_id, db))
            agent_tasks[int_id] = task  # 存储任务对象


async def stop_agents(agent_ids: str):
    ids = agent_ids.split(',')
    for agent_id in ids:
        int_id = int(agent_id)
        if int_id in agent_tasks:
            agent_tasks[int_id].cancel()  # 取消任务
            print(f"Agent {int_id} has been stopped.")
        else:
            print(f"No active agent task found for ID {int_id}.")




