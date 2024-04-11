from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from .database import Base


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



class Memory(Base):
    __tablename__ = "memories"

    memory_id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer)
    memory_type = Column(String)
    related_id = Column(Integer)
    description = Column(String)
    created_time = Column(DateTime)
    embedding = Column(String)

