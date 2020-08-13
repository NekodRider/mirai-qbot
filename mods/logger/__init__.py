from mirai import Mirai, Group, FriendMessage, GroupMessage, MessageChain, Member, Plain, Image, Face, AtAll, At,FlashImage, exceptions
from mirai.logger import Session as SessionLogger
from pathlib import Path


def logger_handler(*args):
    with open(Path(__file__).parent.parent.parent.joinpath("mirai-qbot.log"),"r") as f:
        res = f.readlines()
        res = "".join(res[0 if len(res)<20 else len(res)-20:])
    return [Plain(text=res)]

COMMANDS = {"log":logger_handler}
