import pkgutil
from orbitkit import util
from orbitkit import id_srv
from orbitkit.lark_send import FeiShuTalkChatBot

name = 'orbitkit'

__version__ = (pkgutil.get_data(__package__, "VERSION") or b"").decode("ascii").strip()

__all__ = [
    'util',
    'FeiShuTalkChatBot',
    'id_srv',
]
