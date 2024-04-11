class ChatWithNPC:
    def __init__(self, player_id: int):
        self.player_id = player_id
        self.player_name = ""
        self.player_age = 0
        self.background = ""
        self.character = ""
        self.skill = ""
        self.goal = ""
        self.future = ""
        self.player_sex = ""
        self.load_information()

    def load_information(self) -> None:
        pass