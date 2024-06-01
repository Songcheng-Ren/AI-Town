from sqlalchemy.orm import Session

from .models import Player, Memory, User, Game, Journal


# 查找指定用户
def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


# 插入新用户
def add_user(db: Session, username: str, password: str, salt: str):
    new_user = User(
        username=username,
        password=password,
        salt=salt
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user.user_id  # 返回新添加记录的 ID


# 查找用户的设定
def get_game(db: Session, username: str):
    return db.query(Game).filter(Game.username == username).first()


# 更改用户的剧本
def change_script(db: Session, username: str, new_script: str):
    game = db.query(Game).filter(Game.username == username).first()
    if game:
        game.script = new_script
        db.commit()
        return 1
    else:
        return 0


# 查找指定角色信息
def get_player(db: Session, player_id: int):
    return db.query(Player).filter(Player.player_id == player_id).first()


# 更换人物设定
def change_player(db: Session, player_id: int, player_name: str, player_age: int, background: str, character: str, skill: str, goal: str, future: str, player_sex: str):
    player = db.query(Player).filter(Player.player_id == player_id).first()
    if player:
        player.player_name = player_name
        player.player_age = player_age
        player.background = background
        player.character = character
        player.skill = skill
        player.goal = goal
        player.future = future
        player. player_sex = player_sex
        db.commit()
        return 1
    else:
        return 0


# 添加游戏剧本
def add_game(db: Session, username: str, script: str):
    new_game = Game(
        username=username,
        script=script
    )
    db.add(new_game)
    db.commit()
    db.refresh(new_game)
    return new_game.game_id  # 返回新添加记录的ID


# 添加游戏角色
def add_player(db: Session, player_name: str, player_age: int, background: str, character: str, skill: str, goal: str,
               future: str, player_sex: str, username: str):
    new_player = Player(
        player_name=player_name,
        player_age=player_age,
        background=background,
        character=character,
        skill=skill,
        goal=goal,
        future=future,
        player_sex=player_sex,
        username=username
    )
    db.add(new_player)
    db.commit()
    db.refresh(new_player)
    return new_player.player_id  # 返回新添加记录的ID


# 获得一个玩家所有的npc
def get_all_npc(db: Session, username: str):
    return db.query(Player).filter(Player.username == username).all()


# 查找所有角色
def get_players(db: Session):
    return db.query(Player).all()


# 判断指定角色是否第一次与玩家对话
def is_first_communication(db: Session, player_id: int, other_id: int):
    return db.query(Memory).filter(Memory.player_id == player_id, Memory.related_id == other_id, Memory.memory_type == "relationship").count()


# 查找指定角色的所有的记忆
def get_his_memory(db: Session, player_id: int):
    return db.query(Memory).filter(Memory.player_id == player_id).all()


# 查找指定角色对另一角色的所有认识
def get_memory2other(db: Session, player_id: int, other_id: int):
    return db.query(Memory).filter(Memory.player_id == player_id, Memory.related_id == other_id, Memory.memory_type == "relationship").all()


def add_memory(db: Session, player_id: int, memory_type: str, related_id: int, description: str, created_time: str, embedding_id: str, importance: int):
    new_memory = Memory(
        player_id=player_id,
        memory_type=memory_type,
        related_id=related_id,
        description=description,
        created_time=created_time,
        embedding_id=embedding_id,
        importance=importance
    )
    db.add(new_memory)
    db.commit()
    db.refresh(new_memory)
    print("添加记忆成功！")
    return new_memory.memory_id  # 返回新添加记录的ID


def add_journal(db: Session, journal_data: str, player_id: int, created_time: str):
    new_journal = Journal(
        journal_data=journal_data,
        player_id=player_id,
        created_time=created_time
    )
    db.add(new_journal)
    db.commit()
    db.refresh(new_journal)
    return new_journal.journal_id


def get_journals(db: Session, player_id: int):
    return db.query(Journal) .filter(Journal.player_id == player_id) .order_by(Journal.created_time.desc()).limit(50).all()

# 添加一条新的记录
#  # 返回新添加记录的 ID
# def create_user(db: Session, user: schemas.UserCreate):
#     fake_hashed_password = user.password + "notreallyhashed"
#     db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user


# def get_m(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.Item).offset(skip).limit(limit).all()
#
#
# def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
#     db_item = models.Item(**item.dict(), owner_id=user_id)
#     db.add(db_item)
#     db.commit()
#     db.refresh(db_item)
#     return db_item

