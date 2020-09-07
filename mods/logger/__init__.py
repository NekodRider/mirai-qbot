from mirai import Mirai, Group, FriendMessage, GroupMessage, MessageChain, Member, Plain, Image, Face, AtAll, At,FlashImage, exceptions
from mirai.logger import Session as SessionLogger
from pathlib import Path


async def logger_handler(*args,sender,event_type):
    with open(Path(__file__).parent.parent.parent.joinpath("mirai-qbot.log"),"r") as f:
        res = f.readlines()
        res = "".join(res[0 if len(res)<11 else len(res)-11:len(res)-1])
    return [Plain(text=res)]

COMMANDS = {"log": logger_handler}
