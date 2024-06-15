from typing import Dict

from src.util import GameItem


class UserManager:
    def __init__(self):
        self.users: Dict[str, User] = {}

    def create_user(self):
        user = User()
        self.users[user.id] = user
        return user

    def get(self, id_: str):
        return self.users.get(id_)


class User(GameItem):
    def __init__(self):
        super().__init__()
