from dataclasses import dataclass

from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message

from app import config


@dataclass
class IsSuperuserFilter(BoundFilter):
    key = "is_superuser"
    is_superuser: bool

    async def check(self, message: Message) -> bool:
        return message.from_user.id == config.SUPER_USER_ID
