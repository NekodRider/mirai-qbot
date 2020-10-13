import re
import typing as T
from graia.application.group import Member
from graia.application.friend import Friend
from graia.application.message.chain import MessageChain
from bot import Bot

repeat_queue = [None, None]
repeat_log = [None]
sb_repeat_content = None


def is_equal(a: T.Union[MessageChain, None], b: T.Union[MessageChain, None]):
    if not a or not b:
        return False
    return a.asSerializationString() == b.asSerializationString()


async def repeat_handler(bot: Bot, message: MessageChain,
                         subject: T.Union[Member, Friend]):
    # 复读添加群订阅机制
    if isinstance(subject, Friend):
        return
    global repeat_queue, sb_repeat_content
    pattern = r"^\s*\S{2,6}[SNsn][Bb][!！?？.。]{0,10}\s*$"
    message = message.asSendable()
    message_str = message.asDisplay()
    if re.match(pattern, message_str) and message_str[0] != bot.prefix:
        if not is_equal(sb_repeat_content, message):
            sb_repeat_content = message
            await bot.sendMessage(subject.group, message)
        return
    else:
        sb_repeat_content = message
    if message_str[0] != bot.prefix and is_equal(
            message, repeat_queue[0]) and not is_equal(
                message, repeat_log[0]) and subject != repeat_queue[1]:
        await bot.sendMessage(subject.group, message)
        repeat_queue = [None, None]
        repeat_log[0] = message  #type: ignore
    else:
        repeat_queue = [message, subject]


DIRECTS = {"repeat": repeat_handler}
