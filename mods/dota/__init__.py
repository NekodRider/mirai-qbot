# encoding=Utf-8
from mirai import Mirai, Group, GroupMessage, MessageChain, Member, Plain, Image, Face, AtAll, At, FlashImage, exceptions
from mirai.logger import Session as SessionLogger
from pathlib import Path

from .helper import getDotaPlayerInfo, getDotaGamesInfo, error_codes, dota_dict_path
from .games_24hrs import getGamesIn24Hrs
from .winning_rate import getWinRateGraph, getCompWinRateGraph
from .latest_games import getStat, getLatestComparingStat, getStarStat, getCompStarStat
from .._utils import parseMsg, readJSON, updateJSON
from ..users import getUserInfo


sub_app = Mirai(f"mirai://localhost:8080/?authKey=0&qq=0")
dota_id_dict = readJSON(dota_dict_path)

def args_parser(num, index=None):
    def decorator(func):
        def wrapper(*args,sender,event_type):
            if len(args) < num:
                r = getUserInfo(sender.id)
                userId = r and r['nickname']
                if userId is not None:
                    if index is not None:
                        a = list(args)
                        a.insert(index, userId)
                        args = tuple(a)
                    else:
                        args += (userId, )
            return func(*args,sender = sender,event_type = event_type)
        return wrapper
    return decorator

@args_parser(1)
async def dota_handler(*args,sender, event_type):
    if len(args)!=1:
        return [Plain(text="缺少参数或参数过多")]
    query_id = args[0]
    if query_id not in dota_id_dict.keys():
        SessionLogger.info("[DOTA]未添加该用户")
        return [Plain(text="未添加该用户！")]
    else:
        query_id = dota_id_dict[query_id]
        res = getGamesIn24Hrs(query_id)
        if res in ('请输入正确steam ID!', '该玩家不存在!'):
            SessionLogger.info("[DOTA]"+res)
        else:
            SessionLogger.info("[DOTA]返回成功")
        return [Plain(text=res)]

@args_parser(1,0)
async def stat_handler(*args, sender, event_type):
    if len(args)<1 or len(args)>2:
        return [Plain(text="缺少参数或参数过多")]
    query_id,*num = args
    if query_id not in dota_id_dict.keys():
        SessionLogger.info("[STAT]未添加该用户")
        return [Plain(text="未添加该用户！")]
    else:
        query_id = dota_id_dict[query_id]
        args = 20
        if len(num) == 1:
            try:
                args = int(num[0])
                if args > 50 or args <= 0:
                    args = 20
            except ValueError:
                args = 20
        res = getStat(query_id, args)
        SessionLogger.info("[STAT]返回成功")
        return [Plain(text=res)]

@args_parser(1,0)
async def star_handler(*args, sender, event_type):
    if len(args)<1 or len(args)>2:
        return [Plain(text="缺少参数或参数过多")]
    query_id,*num = args
    if query_id not in dota_id_dict.keys():
        SessionLogger.info("[STAR]未添加该用户")
        return [Plain(text="未添加该用户！")]
    else:
        query_id = dota_id_dict[query_id]
        args = 20
        if len(num) == 1:
            try:
                args = int(num[0])
                if args > 50 or args <= 0:
                    args = 20
            except ValueError:
                args = 20
        pic_name, player_name = getStarStat(query_id, args)
        if type(player_name) == type(0):
            msg = [Plain(text=pic_name)]
            SessionLogger.info("[STAR]用户不存在")
        else:
            msg = [
                Plain(text=player_name + " 最近 " + str(args) + " 场游戏五星图\n"),
                Image.fromFileSystem(pic_name)
            ]
            SessionLogger.info("[STAR]返回成功")
        return msg

@args_parser(2,0)
async def compare_handler(*args, sender, event_type):
    if len(args)<2 or len(args)>3:
        return [Plain(text="缺少参数或参数过多")]
    [id_a,id_b,*num] = args
    if id_a not in dota_id_dict.keys():
        SessionLogger.info("[COMP]未添加用户 "+ id_a)
        return [Plain(text="未添加用户 " + id_a + " ！")]
    elif id_b not in dota_id_dict.keys():
        SessionLogger.info("[COMP]未添加用户 "+ id_b)
        return [Plain(text="未添加用户 " + id_b + " ！")]
    else:
        id_a = dota_id_dict[id_a]
        id_b = dota_id_dict[id_b]
        args = 20
        if len(num)!=0:
            try:
                args = int(num[0])
                if args > 50 or args <= 0:
                    args = 20
            except ValueError:
                args = 20
        res = getLatestComparingStat(id_a, id_b, args)
        msg = [Plain(text=res)]
        SessionLogger.info("[COMP]返回成功")
        return msg

@args_parser(1,0)
async def winrate_handler(*args, sender, event_type):
    if len(args)<1 or len(args)>2:
        return [Plain(text="缺少参数或参数过多")]
    query_id,*num = args
    if query_id not in dota_id_dict.keys():
        SessionLogger.info("[WINRATE]未添加该用户")
        return [Plain(text="未添加该用户！")]
    else:
        query_id = dota_id_dict[query_id]
        args = 20
        if len(num) == 1:
            try:
                args = int(num[0])
                if args > 50 or args <= 0:
                    args = 20
            except ValueError:
                args = 20
        pic_name, player_name = getWinRateGraph(query_id, args)
        if type(player_name) == type(0):
            msg = [Plain(text=pic_name)]
            SessionLogger.info("[WINRATE]用户不存在")
        else:
            msg = [
                Plain(text=player_name + " 最近 " + str(args) + " 场游戏胜率变化图\n"),
                Image.fromFileSystem(pic_name),
            ]
            SessionLogger.info("[WINRATE]返回成功")
        return msg

@args_parser(2,0)
async def setdota_handler(*args, sender, event_type):
    dota_id_dict[args[0]] = args[1]
    updateJSON(dota_dict_path, dota_id_dict)
    return [Plain(text="添加成功！")]

@args_parser(2,0)
async def winrate_compare_handler(*args, sender, event_type):
    args = list(args)
    if len(args)<2:
        return [Plain(text="缺少参数或参数过多")]
    try:
        num = int(args[-1])
        ids = args[:len(args)-1]
    except:
        num = 0
        ids = list(args)
    for no,i in enumerate(ids):
        if i not in dota_id_dict.keys():
            SessionLogger.info("[WRCP]未添加用户 "+ i)
            return [Plain(text="未添加用户 " + i + " ！")]
        ids[no] = dota_id_dict[i]
    else:
        if num<=0 or num > 50:
            num = 20
        pic_name, player_name_list = getCompWinRateGraph(ids, num)
        if type(player_name_list) == type(0):
            msg = [Plain(text=pic_name)]
            SessionLogger.info("[WRCP]用户不存在")
        else:
            msg = [
                Plain(text="最近 " + str(num) + " 场游戏胜率比较图\n"),
                Image.fromFileSystem(pic_name)
            ]
            SessionLogger.info("[WRCP]返回成功")
        return msg

@args_parser(2,0)
async def star_compare_handler(*args, sender, event_type):
    args = list(args)
    if len(args)<2 or len(args)>3:
        return [Plain(text="缺少参数或参数过多")]
    try:
        num = int(args[-1])
        ids = args[:len(args)-1]
    except:
        num = 0
        ids = list(args)
    for no,i in enumerate(ids):
        if i not in dota_id_dict.keys():
            SessionLogger.info("[STCP]未添加用户 "+ i)
            return [Plain(text="未添加用户 " + i + " ！")]
        ids[no] = dota_id_dict[i]
    else:
        if num<=0 or num > 50:
            num = 20
        pic_name, player_name_a, _ = getCompStarStat(ids[0],ids[1], num)
        if type(player_name_a) == type(0):
            msg = [Plain(text=pic_name)]
            SessionLogger.info("[STCP]用户不存在")
        else:
            msg = [
                Plain(text="最近 " + str(num) + " 场游戏数据比较图\n"),
                Image.fromFileSystem(pic_name)
            ]
            SessionLogger.info("[STCP]返回成功")
        return msg

COMMANDS = {"dota": (dota_handler,""), "winrate": (winrate_handler,"胜率图展示"),
            "stat": (stat_handler,"最近数据展示"),
            "setdota": (setdota_handler,"设置dotaid"),"comp": (compare_handler,"最近数据对比"),
            "wrcp": (winrate_compare_handler,"胜率对比"),"star":(star_handler,"五星图展示"),
            "stcp":(star_compare_handler,"五星图对比"),
            }
