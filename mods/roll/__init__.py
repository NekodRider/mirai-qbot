from mirai import Mirai, Group, GroupMessage, MessageChain, Member, Plain, exceptions
from mirai.logger import Session as SessionLogger
import random

sub_app = Mirai(f"mirai://localhost:8080/?authKey=0&qq=0")

@sub_app.receiver("GroupMessage")
async def roll_handler(app: Mirai, group:Group, message:MessageChain, member:Member):
    if message.toString()[:5] == "/roll":
        sender=member.id
        groupId=group.id
        SessionLogger.info("[ROLL]来自群%d中成员%d的消息:" % (groupId,sender),message.toString())
        command = message.toString()[6:]
        params = [int(x) if x!='' else 0 for x in command.split("d")]
        if params[0]>100 or params[1]>999999:
            msg = [Plain(text="参数过大")]
        else:
            res = [random.randint(1,params[1]) for i in range(params[0])]
            msg = [Plain(text="%dd%d 结果:" % tuple(params) + str(res))]
        try:
            await app.sendGroupMessage(group,msg)
        except exceptions.BotMutedError:
            pass