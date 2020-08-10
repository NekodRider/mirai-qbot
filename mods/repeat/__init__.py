from mirai import Mirai, Group, GroupMessage, MessageChain, Member, Plain, Image, Face, AtAll, At,FlashImage, exceptions
import random

sub_app = Mirai(f"mirai://localhost:8080/?authKey=0&qq=0")

repeat_queue = ["",0]
repeat_log = [""]

def stringToMsg(s):
    comps = s.replace("[","]").split("]")
    while '' in comps:
        comps.remove('')
    msg = []
    for i in comps:
        if "Image" in i:
            msg.append(Image(imageId=i.split("::")[-1]))
        #需要修改Face toString方法
        elif "Face" in i:
            msg.append(Face(faceId=i.split("faceId=")[-1]))
        elif "AtAll" in i:
            msg.append(AtAll())
        elif "At" in i:
            msg.append(At(target=i.split("target=")[-1]))
        elif "FlashImage" in i:
            msg.append(FlashImage(imageId=i.split("::")[-1]))
        else:
            msg.append(Plain(text=i))
    return msg

@sub_app.receiver("GroupMessage")
async def repeat_handler(app: Mirai, group:Group, message:MessageChain, member:Member):
    sender=member.id
    groupId=group.id
    if message.toString() == repeat_queue[0] and message.toString() != repeat_log[0] and sender != repeat_queue[1]:
        SessionLogger.info("[REPEAT]来自群%d中成员%d的消息:" % (groupId,sender),message.toString())
        try:
            msg = stringToMsg(message.toString())
            await app.sendGroupMessage(group,msg)
        except exceptions.BotMutedError:
            pass
        repeat_queue=["",0]
        repeat_log[0] = message.toString()
    else:
        repeat_queue = [message.toString(),sender]