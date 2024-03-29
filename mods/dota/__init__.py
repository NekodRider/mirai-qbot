# encoding=Utf-8
# type: ignore
import re
from typing import Union
from pathlib import Path

from bot import Bot
import bot
from bot.logger import defaultLogger as logger
from graia.application.friend import Friend
from graia.application.group import Member
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Image, Plain
from mods._utils.convert import groupFromStr, groupToStr
from mods._utils.storage import readJSON, updateJSON
from mods.user import args_parser

from .diagrams import getCompStarStat, getCompWinRateGraph, getDotaStory, getStarStat, getWinRateGraph
from .process import getGamesIn24Hrs, getLatestComparingStat, getStat
from .helper import getDotaHero


@args_parser(1)
async def dota_handler(*args, bot: Bot, subject: Union[Member, Friend]):
    '''展示最近24小时(上限10场)游戏数据

    用法: /dota (id)'''
    if len(args) != 1:
        return MessageChain.create([Plain(f"缺少参数或参数过多:{args}, 用法: /dota (id)")])
    query_id = args[0]
    if isinstance(subject, Member):
        dota_id = bot.db.get(subject.group, "dota_id").get(query_id)
    else:
        dota_id = bot.db.get(subject, "dota_id").get(query_id)
    if not dota_id:
        logger.info(f"[DOTA]未添加该用户{query_id}")
        return MessageChain.create([Plain(f"未添加该用户{query_id}！")])
    else:
        res = getGamesIn24Hrs(dota_id)
        logger.info("[DOTA]返回成功")
        return MessageChain.create([Plain(f"{res}")])


@args_parser(2, 0)
async def stat_handler(*args, bot: Bot, subject: Union[Member, Friend]):
    '''展示最近指定场数(默认20场)游戏平均数据

    用法: /stat (id) (num)'''
    if len(args) < 1 or len(args) > 2:
        return MessageChain.create(
            [Plain(f"缺少参数或参数过多:{args},用法: /stat (id) (num)")])
    query_id, *num = args
    if isinstance(subject, Member):
        dota_id = bot.db.get(subject.group, "dota_id").get(query_id)
    else:
        dota_id = bot.db.get(subject, "dota_id").get(query_id)
    if not dota_id:
        logger.info(f"[STAT]未添加该用户{query_id}")
        return MessageChain.create([Plain(f"未添加该用户{query_id}！")])
    else:
        if num and type(num[0]) == type(query_id) and query_id == num[0]:
            num = [20]
        query_id = dota_id
        args = 20
        if len(num) == 1:
            try:
                args = int(num[0])
                if args > 50 or args <= 0:
                    args = 20
            except ValueError:
                args = 20
        res = getStat(query_id, args)
        logger.info("[STAT]返回成功")
        return MessageChain.create([Plain(res)])


@args_parser(2, 0)
async def star_handler(*args, bot: Bot, subject: Union[Member, Friend]):
    '''展示最近指定场数(默认20场)游戏五星图数据

    用法: /star (id) (num)'''
    if len(args) < 1 or len(args) > 2:
        return MessageChain.create(
            [Plain(f"缺少参数或参数过多:{args},用法: /star (id) (num)")])
    query_id, *num = args
    if isinstance(subject, Member):
        dota_id = bot.db.get(subject.group, "dota_id").get(query_id)
    else:
        dota_id = bot.db.get(subject, "dota_id").get(query_id)
    if not dota_id:
        logger.info(f"[STAR]未添加该用户{query_id}")
        return MessageChain.create([Plain(f"未添加该用户{query_id}！")])
    else:
        if num and type(num[0]) == type(query_id) and query_id == num[0]:
            num = [20]
        query_id = dota_id
        args = 20
        if len(num) == 1:
            try:
                args = int(num[0])
                if args > 50 or args <= 0:
                    args = 20
            except ValueError:
                args = 20
        pic_name, player_name = getStarStat(query_id, args)
        if isinstance(player_name, int):
            msg = MessageChain.create([Plain(pic_name)])
            logger.info("[STAR]用户不存在")
        else:
            msg = MessageChain.create([
                Plain(player_name + " 最近 " + str(args) + " 场游戏五星图\n"),
                Image.fromLocalFile(pic_name)
            ])
            logger.info("[STAR]返回成功")
        return msg


@args_parser(3, 0)
async def compare_handler(*args, bot: Bot, subject: Union[Member, Friend]):
    '''玩家间最近平均数据对比

    用法: /comp (id_a) id_b (num)'''
    if len(args) < 2 or len(args) > 3:
        return MessageChain.create(
            [Plain(f"缺少参数或参数过多:{args},用法: /comp (id_a) id_b (num)")])
    [id_a, id_b, *num] = args
    if type(id_a) == type(id_b) and id_a == id_b:
        id_b = num[0]
    if isinstance(subject, Member):
        dota_id_a = bot.db.get(subject.group, "dota_id").get(id_a)
        dota_id_b = bot.db.get(subject.group, "dota_id").get(id_b)
    else:
        dota_id_a = bot.db.get(subject, "dota_id").get(id_a)
        dota_id_b = bot.db.get(subject, "dota_id").get(id_b)
    if not dota_id_a:
        logger.info("[COMP]未添加用户 " + id_a)
        return MessageChain.create([Plain("未添加用户 " + id_a + " ！")])
    elif not dota_id_b:
        logger.info("[COMP]未添加用户 " + id_b)
        return MessageChain.create([Plain("未添加用户 " + id_b + " ！")])
    else:
        id_a = dota_id_a
        id_b = dota_id_b
        args = 20
        if len(num) != 0:
            try:
                args = int(num[0])
                if args > 50 or args <= 0:
                    args = 20
            except ValueError:
                args = 20
        res = getLatestComparingStat(id_a, id_b, args)
        msg = MessageChain.create([Plain(res)])
        logger.info("[COMP]返回成功")
        return msg


@args_parser(2, 0)
async def winrate_handler(*args, bot: Bot, subject: Union[Member, Friend]):
    '''最近胜率图展示

    用法: /winrate (id) (num)'''
    if len(args) < 1 or len(args) > 2:
        return MessageChain.create(
            [Plain(f"缺少参数或参数过多:{args},用法: /winrate (id) (num)")])
    query_id, *num = args
    if isinstance(subject, Member):
        dota_id = bot.db.get(subject.group, "dota_id").get(query_id)
    else:
        dota_id = bot.db.get(subject, "dota_id").get(query_id)
    if not dota_id:
        logger.info(f"[WINRATE]未添加该用户{query_id}")
        return MessageChain.create([Plain(f"未添加该用户{query_id}！")])
    else:
        if num and type(num[0]) == type(query_id) and query_id == num[0]:
            num = [20]
        query_id = dota_id
        args = 20
        if len(num) == 1:
            try:
                args = int(num[0])
                if args > 50 or args <= 0:
                    args = 20
            except ValueError:
                args = 20
        pic_name, player_name = getWinRateGraph(query_id, args)
        if isinstance(player_name, int):
            msg = MessageChain.create([Plain(pic_name)])
            logger.info("[WINRATE]用户不存在")
        else:
            msg = MessageChain.create([
                Plain(text=player_name + " 最近 " + str(args) + " 场游戏胜率变化图\n"),
                Image.fromLocalFile(pic_name),
            ])
            logger.info("[WINRATE]返回成功")
        return msg


@args_parser(2, 0)
async def setdota_handler(*args, bot: Bot, subject: Union[Member, Friend]):
    '''设置用户对应的dota id

    用法: /setdota 昵称 数字id'''
    if len(args) != 2:
        return MessageChain.create(
            [Plain(f"缺少参数或参数过多:{args}, 用法: /setdota 昵称 数字id")])
    if re.match(r'^\d+$', args[1]) is None:
        return MessageChain.create([Plain("ID 应由数字组成")])
    if isinstance(subject, Member):
        bot.db.set(subject.group, {"dota_id": {args[0]: args[1]}})
    else:
        bot.db.set(subject, {"dota_id": {args[0]: args[1]}})
    return MessageChain.create([Plain(f"添加成功！{args[0]}->{args[1]}")])


async def winrate_compare_handler(*args, bot: Bot, subject: Union[Member,
                                                                  Friend]):
    '''玩家间最近胜率数据对比
        
    用法: /wrcp id_a id_b (num)'''
    args = list(args)
    if len(args) < 2:
        return MessageChain.create(
            [Plain(f"缺少参数或参数过多:{args},用法: /wrcp id_a id_b (num)")])
    try:
        num = int(args[-1])
        ids = args[:len(args) - 1]
    except ValueError:
        num = 0
        ids = args
    for no, i in enumerate(ids):
        if isinstance(subject, Member):
            dota_id = bot.db.get(subject.group, "dota_id").get(i)
        else:
            dota_id = bot.db.get(subject, "dota_id").get(i)
        if not dota_id:
            logger.info("[WRCP]未添加用户 " + i)
            return MessageChain.create([Plain("未添加用户 " + i + " ！")])
        ids[no] = dota_id
    else:
        if num <= 0 or num > 50:
            num = 20
        pic_name, player_name_list = getCompWinRateGraph(ids, num)
        if type(player_name_list) == type(0):
            msg = MessageChain.create([Plain(pic_name)])
            logger.info("[WRCP]用户不存在")
        else:
            msg = MessageChain.create([
                Plain("最近 " + str(num) + " 场游戏胜率比较图\n"),
                Image.fromLocalFile(pic_name)
            ])
            logger.info("[WRCP]返回成功")
        return msg


@args_parser(2, 0)
async def star_compare_handler(*args, bot: Bot, subject: Union[Member, Friend]):
    '''玩家间最近五星图对比

    用法: /stcp (id_a) id_b (num)'''
    args = list(args)
    if len(args) < 2 or len(args) > 3:
        return MessageChain.create(
            [Plain(f"缺少参数或参数过多:{args},用法: /stcp (id_a) id_b (num)")])
    try:
        num = int(args[-1])
        ids = args[:len(args) - 1]
    except:
        num = 0
        ids = list(args)
    for no, i in enumerate(ids):
        if isinstance(subject, Member):
            dota_id = bot.db.get(subject.group, "dota_id").get(i)
        else:
            dota_id = bot.db.get(subject, "dota_id").get(i)
        if not dota_id:
            logger.info("[STCP]未添加用户 " + i)
            return MessageChain.create([Plain("未添加用户 " + i + " ！")])
        ids[no] = dota_id
    else:
        if num <= 0 or num > 50:
            num = 20
        pic_name, player_name_a, _ = getCompStarStat(ids[0], ids[1], num)
        if isinstance(player_name_a, int):
            msg = MessageChain.create([Plain(pic_name)])
            logger.info("[STCP]用户不存在")
        else:
            msg = MessageChain.create([
                Plain("最近 " + str(num) + " 场游戏数据比较图\n"),
                Image.fromLocalFile(pic_name)
            ])
            logger.info("[STCP]返回成功")
        return msg


@args_parser(2, 0)
async def hero_handler(*args, bot: Bot, subject: Union[Member, Friend]):
    '''展示玩家英雄平均数据

    用法: /hero (id) 英雄名'''
    if len(args) != 2:
        return MessageChain.create(
            [Plain(f"缺少参数或参数过多:{args},用法: /hero (id) 英雄名")])
    query_id = args[0]
    if isinstance(subject, Member):
        dota_id = bot.db.get(subject.group, "dota_id").get(query_id)
    else:
        dota_id = bot.db.get(subject, "dota_id").get(query_id)
    if not dota_id:
        logger.info(f"[HERO]未添加该用户{query_id}")
        return MessageChain.create([Plain(f"未添加该用户{query_id}！")])
    else:
        query_id = dota_id
        res = getDotaHero(query_id, args[1])
        if isinstance(res, tuple):
            res = res[1]
            logger.info("[HERO]返回成功")
        elif res == 0:
            res = f"参数有误:{args[1]}"
            logger.info(f"[HERO]参数有误:{args[1]}")
        else:
            logger.info("[HERO]返回成功")
        return MessageChain.create([Plain(res)])


async def story_handler(*args, bot: Bot, subject: Union[Member, Friend]):
    '''dota战报展示

    用法: /story 比赛id'''
    if len(args) != 1:
        return MessageChain.create([Plain(f"缺少参数或参数过多:{args},用法: /story 比赛id")])
    match_id = args[0]
    path = await getDotaStory(match_id)
    msg = None
    if not isinstance(path, str):
        if path == 404:
            msg = MessageChain.create([Plain(f"未找到比赛:{match_id}")])
            logger.info(f"[STORY]未找到比赛:{match_id}")
        elif path == 1:
            msg = MessageChain.create([Plain(f"比赛{match_id}解析中，请等待2min后重试")])
            logger.info(f"[STORY]解析中:{match_id}")
    else:
        msg = MessageChain.create([Image.fromLocalFile(path)])
        logger.info("[STORY]返回成功")
    return msg


COMMANDS = {
    "dota": dota_handler,
    "winrate": winrate_handler,
    "stat": stat_handler,
    "setdota": setdota_handler,
    "comp": compare_handler,
    "wrcp": winrate_compare_handler,
    "star": star_handler,
    "stcp": star_compare_handler,
    "hero": hero_handler,
    "story": story_handler
}

SCHEDULES = {}
