from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain
from pathlib import Path

async def logger_handler(*args, subject):
    with open(Path(__file__).parent.parent.parent.joinpath("logs","mirai_bot.log"),"r",encoding='utf-8') as f:
        res = f.readlines()
        res = "".join(res[0 if len(res)<21 else len(res)-21:len(res)-1])
    return MessageChain.create([Plain(res)])

COMMANDS = {"log": logger_handler}
