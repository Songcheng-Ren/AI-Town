from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    password = Column(String)
    salt = Column(String)


class Player(Base):
    __tablename__ = "players"

    player_id = Column(Integer, primary_key=True, autoincrement=True)
    player_name = Column(String)
    player_age = Column(Integer)
    background = Column(String)
    character = Column(String)
    skill = Column(String)
    goal = Column(String)
    future = Column(String)
    player_sex = Column(String)
    username = Column(String)


class Memory(Base):
    __tablename__ = "memories"

    memory_id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer)
    memory_type = Column(String)
    related_id = Column(Integer)
    description = Column(String)
    created_time = Column(String)
    embedding_id = Column(String)
    importance = Column(Integer)

class Game(Base):
    __tablename__ = "game"

    game_id = Column(Integer, primary_key=True, autoincrement=True)
    script = Column(String)
    game_data = Column(String)
    username = Column(String)
    development = Column(String)

class Journal(Base):
    __tablename__ = "journal"

    journal_id = Column(Integer, primary_key=True, autoincrement=True)
    journal_data = Column(String)
    player_id = Column(Integer)
    created_time = Column(String)

class Agent_db(Base):
    __tablename__ = "agent"

    player_id = Column(Integer, primary_key=True)
    wake = Column(Integer)
    scheduled = Column(Integer)
    action = Column(String(4096))
    thinking = Column(Integer)
    interactive = Column(Integer)
    update_time = Column(String(255))
