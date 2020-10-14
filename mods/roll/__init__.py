from graia.application.message.elements.internal import Plain
from graia.application.message.chain import MessageChain
from graia.application.group import Member
from graia.application.friend import Friend
import typing as T
import random
import re


async def roll_handler(*args, subject: T.Union[Member, Friend]):
    '''按照所给参数roll点

    用法: /roll 参数 如/roll 2d6+4代表 roll 2次6面骰子再加4 '''
    params = args
    if len(args) < 1:
        return MessageChain.create([Plain("缺少参数")])
    msg = [Plain("\n")]
    for arg in args:
        res = re.match(r"(\d+d\d+)(\+\d+)*", arg)
        if not res:
            return MessageChain.create([Plain("参数格式不对 请输入 2d6+4 形式")])
        d, p = res[1], res[2]
        param = [int(x) if x != '' else 0 for x in d.split("d")]
        if param[0] > 100 or param[1] > 999999 or 0 in param:
            msg.append(Plain(f"{param[0]}d{param[1]} 参数为0或过大\n"))
            continue
        res = [random.randint(1, param[1]) for _ in range(param[0])]
        msg.append(
            Plain(
                f"{param[0]}d{param[1]}{p or ''} 结果:{str(res)}{p or ''}{' = '+str(sum(res))+(p or '') if param[0]>1 else ''}{' = '+str(sum(res)+int(p)) if p else ''}\n"
            ))

    return MessageChain.create(msg)



COMMANDS = {"roll": roll_handler}
