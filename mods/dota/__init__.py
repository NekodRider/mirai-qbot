# encoding=Utf-8
# type: ignore
import re
import typing as T
from pathlib import Path

from bot import Bot
from bot.logger import defaultLogger as logger
from graia.application.friend import Friend
from graia.application.group import Member
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Image, Plain
from mods._utils.convert import groupFromStr, groupToStr
from mods._utils.storage import readJSON, updateJSON
from mods.user import args_parser

from .diagrams import (getCompStarStat, getCompWinRateGraph, getDotaStory,
                       getStarStat, getWinRateGraph)
from .games import getGamesIn24Hrs, getLatestComparingStat, getStat
from .helper import dota_dict_path, getDotaHero, getDotaNews

NEWS_JSON_PATH = Path(__file__).parent.joinpath("news.json")
dota_id_dict = readJSON(dota_dict_path)
if not isinstance(dota_id_dict, dict):
    raise TypeError("Expected dict but found:", dota_id_dict)


@args_parser(1)
async def dota_handler(*args, subject: T.Union[Member, Friend]):
    '''展示最近24小时(上限10场)游戏数据

    用法: /dota (id)'''
    if len(args) != 1:
        return MessageChain.create([Plain(f"缺少参数或参数过多:{args}, 用法: /dota (id)")])
    query_id = args[0]
    if query_id not in dota_id_dict.keys():
        logger.info(f"[DOTA]未添加该用户{query_id}")
        return MessageChain.create([Plain(f"未添加该用户{query_id}！")])
    else:
        query_id = dota_id_dict[query_id]
        res = getGamesIn24Hrs(query_id)
        if res in ('请输入正确steam ID!', '该玩家不存在!'):
            logger.info("[DOTA]" + res)
        else:
            logger.info("[DOTA]返回成功")
        return MessageChain.create([Plain(res)])


@args_parser(2, 0)
async def stat_handler(*args, subject: T.Union[Member, Friend]):
    '''展示最近指定场数(默认20场)游戏平均数据

    用法: /stat (id) (num)'''
    if len(args) < 1 or len(args) > 2:
        return MessageChain.create(
            [Plain(f"缺少参数或参数过多:{args},用法: /stat (id) (num)")])
    query_id, *num = args
    if query_id not in dota_id_dict.keys():
        logger.info(f"[STAT]未添加该用户{query_id}")
        return MessageChain.create([Plain(f"未添加该用户{query_id}！")])
    else:
        if num and type(num[0]) == type(query_id) and query_id == num[0]:
            num = [20]
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
        logger.info("[STAT]返回成功")
        return MessageChain.create([Plain(res)])


@args_parser(2, 0)
async def star_handler(*args, subject: T.Union[Member, Friend]):
    '''展示最近指定场数(默认20场)游戏五星图数据

    用法: /star (id) (num)'''
    if len(args) < 1 or len(args) > 2:
        return MessageChain.create(
            [Plain(f"缺少参数或参数过多:{args},用法: /star (id) (num)")])
    query_id, *num = args
    if query_id not in dota_id_dict.keys():
        logger.info(f"[STAR]未添加该用户{query_id}")
        return MessageChain.create([Plain(f"未添加该用户{query_id}！")])
    else:
        if num and type(num[0]) == type(query_id) and query_id == num[0]:
            num = [20]
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
async def compare_handler(*args, subject: T.Union[Member, Friend]):
    '''玩家间最近平均数据对比

    用法: /comp (id_a) id_b (num)'''
    if len(args) < 2 or len(args) > 3:
        return MessageChain.create(
            [Plain(f"缺少参数或参数过多:{args},用法: /comp (id_a) id_b (num)")])
    [id_a, id_b, *num] = args
    if type(id_a) == type(id_b) and id_a == id_b:
        id_b = num[0]
    if id_a not in dota_id_dict.keys():
        logger.info("[COMP]未添加用户 " + id_a)
        return MessageChain.create([Plain("未添加用户 " + id_a + " ！")])
    elif id_b not in dota_id_dict.keys():
        logger.info("[COMP]未添加用户 " + id_b)
        return MessageChain.create([Plain("未添加用户 " + id_b + " ！")])
    else:
        id_a = dota_id_dict[id_a]
        id_b = dota_id_dict[id_b]
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
async def winrate_handler(*args, subject: T.Union[Member, Friend]):
    '''最近胜率图展示

    用法: /winrate (id) (num)'''
    if len(args) < 1 or len(args) > 2:
        return MessageChain.create(
            [Plain(f"缺少参数或参数过多:{args},用法: /winrate (id) (num)")])
    query_id, *num = args
    if query_id not in dota_id_dict.keys():
        logger.info(f"[WINRATE]未添加该用户{query_id}")
        return MessageChain.create([Plain(f"未添加该用户{query_id}！")])
    else:
        if num and type(num[0]) == type(query_id) and query_id == num[0]:
            num = [20]
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
async def setdota_handler(*args, subject: T.Union[Member, Friend]):
    '''设置用户对应的dota id

    用法: /setdota 昵称 数字id'''
    if len(args) != 2:
        return MessageChain.create(
            [Plain(f"缺少参数或参数过多:{args}, 用法: /setdota 昵称 数字id")])
    if re.match(r'^\d+$', args[1]) is None:
        return MessageChain.create([Plain("ID 应由数字组成")])
    dota_id_dict[args[0]] = args[1]
    updateJSON(dota_dict_path, dota_id_dict)
    return MessageChain.create([Plain(f"添加成功！{args[0]}->{args[1]}")])


async def winrate_compare_handler(*args, subject: T.Union[Member, Friend]):
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
        if i not in dota_id_dict.keys():
            logger.info("[WRCP]未添加用户 " + i)
            return MessageChain.create([Plain("未添加用户 " + i + " ！")])
        ids[no] = dota_id_dict[i]
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
async def star_compare_handler(*args, subject: T.Union[Member, Friend]):
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
        if i not in dota_id_dict.keys():
            logger.info("[STCP]未添加用户 " + i)
            return MessageChain.create([Plain("未添加用户 " + i + " ！")])
        ids[no] = dota_id_dict[i]
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


async def dotanews_handler(*args, subject: T.Union[Member, Friend]):
    '''DOTA新闻订阅

    用法: /dotanews'''
    news_dict = readJSON(NEWS_JSON_PATH)
    if not isinstance(news_dict, dict):
        raise TypeError("Expected dict but found:", news_dict)
    if isinstance(subject, Member) and groupToStr(
            subject.group) not in news_dict["member"]:
        news_dict["member"].append(groupToStr(subject.group))
    if isinstance(subject, Friend) and subject.id not in news_dict["member"]:
        news_dict["member"].append(subject.id)
    updateJSON(NEWS_JSON_PATH, news_dict)
    msg = MessageChain.create([Plain("已订阅DOTA新闻\n")])
    logger.info("[DOTANEWS]返回成功")
    return msg


async def rmdotanews_handler(*args, subject: T.Union[Member, Friend]):
    '''DOTA新闻取消订阅

    用法: /rmdotanews'''
    news_dict = readJSON(NEWS_JSON_PATH)
    if not isinstance(news_dict, dict):
        raise TypeError("Expected dict but found:", news_dict)
    if isinstance(subject, Member) and groupToStr(
            subject.group) in news_dict["member"]:
        news_dict["member"].remove(groupToStr(subject.group))
    elif isinstance(subject, Friend) and subject.id in news_dict["member"]:
        news_dict["member"].remove(subject.id)
    if len(news_dict["member"]) == 0:
        del news_dict["member"]
    updateJSON(NEWS_JSON_PATH, news_dict)
    msg = MessageChain.create([Plain("已取消订阅DOTA新闻\n")])
    logger.info("[RMDOTANEWS]返回成功")
    return msg


@args_parser(2, 0)
async def hero_handler(*args, subject: T.Union[Member, Friend]):
    '''展示玩家英雄平均数据

    用法: /hero (id) 英雄名'''
    if len(args) != 2:
        return MessageChain.create(
            [Plain(f"缺少参数或参数过多:{args},用法: /hero (id) 英雄名")])
    query_id = args[0]
    if query_id not in dota_id_dict.keys():
        logger.info(f"[HERO]未添加该用户{query_id}")
        return MessageChain.create([Plain(f"未添加该用户{query_id}！")])
    else:
        query_id = dota_id_dict[query_id]
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


async def story_handler(*args, subject: T.Union[Member, Friend]):
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


async def news_scheduler(bot: Bot):
    news_dict = readJSON(NEWS_JSON_PATH, defaultValue={"member": []})
    if not isinstance(news_dict, dict):
        raise TypeError("Expected dict but found:", news_dict)
    news = getDotaNews()
    if len(news) > 0:
        msg = []
        for i in news:
            img = []
            res = f"\n{i['title']}\n"
            if "[img]" in i["contents"]:
                pattern = r"\[img\][\S]*\[/img\]"
                imgs = re.findall(pattern, i["contents"])
                img.append(Image.fromNetworkAddress(imgs[0][5:-6]))
                for to_rm in imgs:
                    i["contents"] = i["contents"].replace(to_rm, "")
                res += i["contents"].strip() + "\n\n"
            msg += img
            msg.append(Plain(text=res))
        msg = MessageChain.create(msg)
        for member in news_dict["member"]:
            if type(member) == str:
                await bot.sendMessage(groupFromStr(member), msg)
            else:
                await bot.sendMessage(member, msg)


COMMANDS = {
    "dota": dota_handler,
    "winrate": winrate_handler,
    "stat": stat_handler,
    "setdota": setdota_handler,
    "comp": compare_handler,
    "wrcp": winrate_compare_handler,
    "star": star_handler,
    "stcp": star_compare_handler,
    "dotanews": dotanews_handler,
    "rmdotanews": rmdotanews_handler,
    "hero": hero_handler,
    "story": story_handler
}

SCHEDULES = {
    "DOTA更新订阅": {
        "func": news_scheduler,
        "interval": 300
    },
}
