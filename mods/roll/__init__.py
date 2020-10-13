from graia.application.message.elements.internal import Plain
from graia.application.message.chain import MessageChain
from graia.application.group import Member
from graia.application.friend import Friend
import typing as T
import random


async def roll_handler(*args, subject: T.Union[Member, Friend]):
    '''按照所给参数roll点

    用法: /roll 参数 如/roll 2d6代表 roll 2次6面骰子 '''
    params = args
    if len(args) != 1:
        return MessageChain.create([Plain("缺少参数或参数过多")])
    if "d" not in args[0]:
        return MessageChain.create([Plain("参数格式不对 请输入1d6形式")])
    param = [int(x) if x != '' else 0 for x in params[0].split("d")]
    if param[0] > 100 or param[1] > 999999:
        return MessageChain.create([Plain("参数过大")])
    res = [random.randint(1, param[1]) for i in range(param[0])]
    msg = MessageChain.create([Plain("%dd%d 结果:" % tuple(param) + str(res))])
    return msg


COMMANDS = {"roll": roll_handler}
