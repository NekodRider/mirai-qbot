from mirai import Mirai, Group, GroupMessage, MessageChain, Member, Plain, exceptions
from mirai.logger import Session as SessionLogger
import random


def roll_handler(*args,sender,event_type):
    params = args
    if len(args)!=1:
        return [Plain(text="缺少参数或参数过多")]
    if "d" not in args[0]:
        return [Plain(text="参数格式不对 请输入1d6形式")]
    param = [int(x) if x!='' else 0 for x in params[0].split("d")]
    if param[0]>100 or param[1]>999999:
        return [Plain(text="参数过大")]
    res = [random.randint(1,param[1]) for i in range(param[0])]
    msg = [Plain(text="%dd%d 结果:" % tuple(param) + str(res))]
    return msg

COMMANDS = {"roll":roll_handler}
