import re
from typing import Union

from graia.application.friend import Friend
from graia.application.group import Member
from graia.application.message.chain import MessageChain

from bot import Bot

repeat_queue = [None, None]
repeat_content = None
sb_repeat_content = None


def is_equal(a: Union[MessageChain, None], b: Union[MessageChain, None]):
    if not a or not b:
        return False
    return a.asSerializationString() == b.asSerializationString()


async def repeat_handler(message: MessageChain, bot: Bot,
                         subject: Union[Member, Friend]):
    '''bot拟人化, 实现人类的本质.
    
    开启后会自动参与复读以及吹比'''
    message = message.asSendable()
    message_str = message.asDisplay()
    if isinstance(subject, Friend) or not message_str:
        return

    global repeat_queue, sb_repeat_content, repeat_content

    if re.match(r"^\s*\S{2,6}[SNsn][Bb][!！?？.。]{0,10}\s*$",
                message_str) and message_str[0] != bot.prefix:
        if not is_equal(sb_repeat_content, message):
            sb_repeat_content = message
            await bot.sendMessage(subject, message, withAt=False)
        return
    else:
        sb_repeat_content = message
    if message_str[0] != bot.prefix and is_equal(
            message, repeat_queue[0]) and not is_equal(
                message, repeat_content) and subject != repeat_queue[1]:
        await bot.sendMessage(subject, message, withAt=False)
        repeat_queue = [None, None]
        repeat_content = message
    else:
        repeat_queue = [message, subject]


DIRECTS = {"复读": repeat_handler}
