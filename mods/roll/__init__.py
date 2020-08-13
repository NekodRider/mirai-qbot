from mirai import Mirai, Group, GroupMessage, MessageChain, Member, Plain, exceptions
from mirai.logger import Session as SessionLogger
import random


def roll_handler(*args):
    params = args
    param = [int(x) if x!='' else 0 for x in params[0].split("d")]
    if param[0]>100 or param[1]>999999:
        msg = [Plain(text="参数过大")]
    else:
        res = [random.randint(1,param[1]) for i in range(param[0])]
        msg = [Plain(text="%dd%d 结果:" % tuple(param) + str(res))]
    return msg

COMMANDS = {"roll":roll_handler}
