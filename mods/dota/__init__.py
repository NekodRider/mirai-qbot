#encoding=Utf-8
from mirai import Mirai, Group, GroupMessage, MessageChain, Member, Plain, Image, Face, AtAll, At,FlashImage, exceptions

from .helper import readDict, updateDict, getDotaInfo

sub_app = Mirai(f"mirai://localhost:8080/?authKey=0&qq=0")

dota_id_dict = readDict()

@sub_app.receiver("GroupMessage")
async def dota_handler(app: Mirai, group:Group, message:MessageChain, member:Member):
    if message.toString()[:5] == "/dota":
        query_id = message.toString()[6:]
        if query_id in dota_id_dict.keys():
            query_id = dota_id_dict[query_id]
        res = getDotaInfo(query_id)
        msg = [Plain(text=res)]
        try:
            await app.sendGroupMessage(group,msg)
        except exceptions.BotMutedError:
            pass
    elif message.toString()[:8] == "/setdota":
        rec = message.toString()[9:].split(" ")
        dota_id_dict[rec[0]] = rec[1]
        updateDict(dota_id_dict)
        msg = [Plain(text="添加成功！")]
        try:
            await app.sendGroupMessage(group,msg)
        except exceptions.BotMutedError:
            pass
