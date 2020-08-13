# encoding=Utf-8
from mirai import Mirai, Group, GroupMessage, MessageChain, Member, Plain, Image, Face, AtAll, At, FlashImage, exceptions
from mirai.logger import Session as SessionLogger
from .helper import getDotaPlayerInfo, getDotaGamesInfo, error_codes, dota_dict_path
from .games_24hrs import getGamesIn24Hrs
from .winning_rate import getWinningRateGraph
from .latest_games import getLatestGamesStat, getLatestComparingStat
from pathlib import Path
from utils.dict_loader import readDict, updateDict
from mods.users.user_info_loader import getUserInfo
from utils.msg_parser import parseMsg

sub_app = Mirai(f"mirai://localhost:8080/?authKey=0&qq=0")
dota_id_dict = readDict(dota_dict_path)

COMMANDS_FLAG = False

# 理论上应该规定一下handler的类型，算了随便搞好了


def addDefaultQueryIdWhileLT(num, index=None):
    def dec(func):
        def wrapper(*args):
            if len(args) < num:
                r = getUserInfo(args[0])
                userId = r and r['nickname']
                if userId is not None:
                    if index is not None:
                        a = list(args)
                        a.insert(index, userId)
                        args = tuple(a)
                    else:
                        args += (userId, )
            return func(*args)
        return wrapper
    return dec


@addDefaultQueryIdWhileLT(3)
def dotaDotaHandler(sender, groupId, *args):
    query_id = args[0] if len(args) > 0 else None
    if query_id not in dota_id_dict.keys():
        SessionLogger.info("[DOTA]未添加该用户")
        return "未添加该用户！"
    else:
        query_id = dota_id_dict[query_id]
        res = getGamesIn24Hrs(query_id)
        if res in ('请输入正确steam ID!', '该玩家不存在!'):
            SessionLogger.info("[DOTA]"+res)
        else:
            SessionLogger.info("[DOTA]返回成功")
        return res


@addDefaultQueryIdWhileLT(3)
def statHandler(sender, groupId, *args):
    query_id =  list(args)
    if query_id[0] not in dota_id_dict.keys():
        SessionLogger.info("[STAT]未添加该用户")
        return "未添加该用户！"
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
        res = getLatestGamesStat(query_id[0], args)
        SessionLogger.info("[STAT]返回成功")
        return res


@addDefaultQueryIdWhileLT(4, 2)
def compHandler(sender, groupId, *args):
    query_id = list(args)
    if query_id[0] not in dota_id_dict.keys():
        SessionLogger.info("[COMP]未添加该用户")
        return "未添加用户" + query_id[0] + "！"
    elif query_id[1] not in dota_id_dict.keys():
        SessionLogger.info("[COMP]未添加该用户")
        return "未添加用户" + query_id[1] + "！"
    else:
        query_id[0] = dota_id_dict[query_id[0]]
        query_id[1] = dota_id_dict[query_id[1]]
        args = 20
        if len(query_id) == 3:
            try:
                args = int(query_id[2])
                if args > 50 or args <= 0:
                    args = 20
            except ValueError:
                args = 20
        res = getLatestComparingStat(query_id[0], query_id[1], args)
        SessionLogger.info("[COMP]返回成功")
        return res


@addDefaultQueryIdWhileLT(3)
def winrateHandler(sender, groupId, *args):
    query_id = list(args)
    if query_id[0] not in dota_id_dict.keys():
        SessionLogger.info("[WINRATE]未添加该用户")
        return "未添加该用户！"
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
        return msg


@addDefaultQueryIdWhileLT(4, 2)
def setDotaHandler(sender, groupId, *args):
    dota_id_dict[args[0]] = args[1]
    updateDict(dota_dict_path, dota_id_dict)
    return [Plain(text="添加成功！")]


DOTA_Handlers = {
    'dota': dotaDotaHandler,
    'stat': statHandler,
    'comp': compHandler,
    'winrate': winrateHandler,
    'setdota': setDotaHandler,

}


@sub_app.receiver("GroupMessage")
async def dota_handler(app: Mirai, group: Group, message: MessageChain, member: Member):
    [cmd, *args] = parseMsg(message.toString())
    if cmd not in DOTA_Handlers.keys():
        return

    SessionLogger.info("[%s]群%d中%d消息:" %
                       (cmd.upper(), group.id, member.id) + cmd + ' ' + ' '.join(args))

    handler = DOTA_Handlers[cmd]
    r = handler(member.id, group.id, *args)
    msg = [Plain(text=r)]if type(r) == str else r
    try:
        await app.sendGroupMessage(group, msg)
    except exceptions.BotMutedError:
        pass
