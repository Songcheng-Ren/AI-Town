from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt
from sql.database import get_db
from sql.models import User
from sql.schemas import UserCreate
from sql import crud
import base64
import hashlib
import os
import json
from agent.utils.llm import LLMCaller
from agent.prompt.prompt import Prompt
router = APIRouter()

# 定义JWT相关的常量
SECRET_KEY = "YOUR_SECRET_KEY"  # 生产环境中应通过环境变量安全存储
ALGORITHM = "HS256"  # 使用的JWT编码算法
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 访问令牌的有效期限

# 使用OAuth2作为认证方案，`tokenUrl`指定获取token的API路径
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def generate_salt():
    # 生成一个随机盐值
    return base64.b64encode(os.urandom(16)).decode('utf-8')


def hash_password(password: str, salt: str):
    # 使用SHA-256和盐值对密码进行散列
    salted_password = salt + password
    return hashlib.sha256(salted_password.encode()).hexdigest()


def verify_password(plain_password, salt, hashed_password):
    # 验证明文密码和散列密码是否匹配
    return hash_password(plain_password, salt) == hashed_password


def create_access_token(data: dict, expires_delta: timedelta = None):
    # 创建JWT令牌
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # 注册新用户，存储用户名、盐值和散列后的密码
    existing_user = crud.get_user(db, username=user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    salt = generate_salt()
    hashed_password = hash_password(user.password, salt)
    new_user = crud.add_user(db, username=user.username, password=hashed_password, salt=salt)
    default_script = crud.get_game(db, username="0")
    crud.add_game(db, username=user.username, script=default_script.script)
    default_setting = crud.get_all_npc(db, username="0")
    for i in range(5):
        player_name = default_setting[i].player_name
        player_sex = default_setting[i].player_sex
        player_age = default_setting[i].player_age
        background = default_setting[i].background
        character = default_setting[i].character
        skill = default_setting[i].skill
        goal = default_setting[i].goal
        future = default_setting[i].future
        crud.add_player(db, player_name=player_name, player_age=player_age, background=background, character=character,
                        skill=skill, goal=goal, future=future, player_sex=player_sex, username=user.username)
    return {"message": "User successfully registered", "user_id": new_user}


@router.post("/login")
async def login(user: UserCreate, db: Session = Depends(get_db)):
    # 用户登录，验证用户名和密码，返回JWT
    db_user = crud.get_user(db, username=user.username)
    if not db_user or not verify_password(user.password, db_user.salt, db_user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    players = crud.get_all_npc(db, username=user.username)
    npc_id = ""
    npc_name = ""
    for player in players:
        npc_id = npc_id + str(player.player_id) + ","
        npc_name = npc_name + player.player_name + ","
    npc_id = npc_id[:-1]
    npc_name = npc_name[:-1]
    return {"access_token": access_token, "token_type": "bearer", "username": user.username, "npc_id": npc_id, "npc_name": npc_name}


@router.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # 验证JWT，并返回用户信息
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        db_user = crud.get_user(db, username=username)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"username": username, "user": {"id": db_user.id, "username": db_user.username}}
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

