from mirai import Mirai, Group, GroupMessage, MessageChain, Member, Plain, Image, Face, AtAll, At,FlashImage, exceptions
from mirai.logger import Session as SessionLogger
from .._utils import stringToMsg
from .. import PREFIX
import random
import re

sub_app = Mirai(f"mirai://localhost:8080/?authKey=0&qq=0")

repeat_queue = ["",0]
repeat_log = [""]

@sub_app.receiver("GroupMessage")
async def repeat_handler(app: Mirai, group:Group, message:MessageChain, member:Member):
    sender=member.id
    groupId=group.id
    global repeat_queue
    pattern = "^\s*\S{2,6}[SNsn][Bb][!！?？.。]{0,10}\s*$"
    if re.match(pattern, message.toString()):
        try:
            msg = stringToMsg(message.toString())
            await app.sendGroupMessage(group,msg)
        except exceptions.BotMutedError:
            pass
        return
    if message.toString()[0]!=PREFIX and message.toString() == repeat_queue[0] and message.toString() != repeat_log[0] and sender != repeat_queue[1]:
        SessionLogger.info("[REPEAT]来自群%d中成员%d的消息:" % (groupId,sender) + message.toString())
        try:
            msg = stringToMsg(message.toString())
            await app.sendGroupMessage(group,msg)
        except exceptions.BotMutedError:
            pass
        repeat_queue=["",0]
        repeat_log[0] = message.toString()
    else:
        repeat_queue = [message.toString(),sender]
