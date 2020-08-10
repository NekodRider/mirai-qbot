#encoding=Utf-8
from mirai import Mirai, Group, GroupMessage, MessageChain, Member, Plain, Image, Face, AtAll, At,FlashImage, exceptions
from .helper import readDict, updateDict, getDotaPlayerInfo, getDotaGamesInfo, error_codes
from .games_24hrs import getGamesIn24Hrs
from .winning_rate import getWinningRateGraph
from pathlib import Path

sub_app = Mirai(f"mirai://localhost:8080/?authKey=0&qq=0")
dota_id_dict = readDict()


@sub_app.receiver("GroupMessage")
async def dota_handler(app: Mirai, group:Group, message:MessageChain, member:Member):
    sender=member.id
    groupId=group.id
    if message.toString()[:5] == "/dota":
        SessionLogger.info("[DOTA]来自群%d中成员%d的消息:" % (groupId,sender),message.toString())
        query_id = message.toString()[6:]
        if query_id not in dota_id_dict.keys():
            msg = [Plain(text="未添加该用户！")]
            SessionLogger.info("[DOTA]未添加该用户")
        else:
            query_id = dota_id_dict[query_id]
            res = getGamesIn24Hrs(query_id)
            msg = [Plain(text=res)]
            SessionLogger.info("[DOTA]返回成功")
        try:
            await app.sendGroupMessage(group,msg)
        except exceptions.BotMutedError:
            pass
    elif message.toString()[:8] == "/winrate":
        SessionLogger.info("[WINRATE]来自群%d中成员%d的消息:" % (groupId,sender),message.toString())
        query_id = message.toString()[9:].split(" ")
        if query_id[0] not in dota_id_dict.keys():
            msg = [Plain(text="未添加该用户！")]
            SessionLogger.info("[WINRATE]未添加该用户")
        else:
            query_id[0] = dota_id_dict[query_id[0]]
            args = 20
            if len(query_id) == 2:
                try:
                    args = int(query_id[1])
                    if args > 50 or args <= 0:
                        args = 20
                except ValueError:
                    args = 20
            pic_name, player_name = getWinningRateGraph(query_id[0], args)
            if type(player_name) == type(0):
                msg = [Plain(text=pic_name)]
                SessionLogger.info("[WINRATE]用户不存在")
            else:
                msg = [
                    Image.fromFileSystem(pic_name),
                    Plain(text=player_name + "最近" + str(args) + "场游戏胜率变化图")
                ]
                SessionLogger.info("[WINRATE]返回成功")
        try:
            await app.sendGroupMessage(group,msg)
        except exceptions.BotMutedError:
            pass
    elif message.toString()[:8] == "/setdota":
        SessionLogger.info("[SETDOTA]来自群%d中成员%d的消息:" % (groupId,sender),message.toString())
        rec = message.toString()[9:].split(" ")
        dota_id_dict[rec[0]] = rec[1]
        updateDict(dota_id_dict)
        msg = [Plain(text="添加成功！")]
        try:
            await app.sendGroupMessage(group,msg)
        except exceptions.BotMutedError:
            pass
