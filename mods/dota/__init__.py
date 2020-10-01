# encoding=Utf-8
import sys
import re

from mirai import Mirai, Group, GroupMessage, MessageChain, Member, Plain, Image, Face, AtAll, At, FlashImage, exceptions
from mirai.logger import Session as SessionLogger
from pathlib import Path

from .helper import dota_dict_path, getDotaNews, getDotaHero
from .games_24hrs import getGamesIn24Hrs
from .winning_rate import getWinRateGraph, getCompWinRateGraph
from .latest_games import getStat, getLatestComparingStat, getStarStat, getCompStarStat
from .story import getDotaStory
from .._utils import readJSON, updateJSON, groupFromStr, groupToStr, args_parser, schedule_task, api_cache
from .. import message_queue

sub_app = Mirai(f"mirai://localhost:8080/?authKey=0&qq=0")
NEWS_JSON_PATH = Path(__file__).parent.joinpath("news.json")
dota_id_dict = readJSON(dota_dict_path)


@args_parser(1)
async def dota_handler(*args, sender, event_type):
    '''展示最近24小时(上限10场)游戏数据

    用法: /dota (id)'''
    if len(args) != 1:
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


@args_parser(1, 0)
async def stat_handler(*args, sender, event_type):
    '''展示最近指定场数(默认20场)游戏平均数据

    用法: /stat 或 /stat id (num)'''
    if len(args) < 1 or len(args) > 2:
        return [Plain(text="缺少参数或参数过多")]
    query_id, *num = args
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


@args_parser(1, 0)
async def star_handler(*args, sender, event_type):
    '''展示最近指定场数(默认20场)游戏五星图数据

    用法: /star 或 /star id (num)'''
    if len(args) < 1 or len(args) > 2:
        return [Plain(text="缺少参数或参数过多")]
    query_id, *num = args
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


@args_parser(2, 0)
async def compare_handler(*args, sender, event_type):
    '''玩家间最近平均数据对比

    用法: /comp id_b 或 /comp id_a id_b (num)'''
    if len(args) < 2 or len(args) > 3:
        return [Plain(text="缺少参数或参数过多")]
    [id_a, id_b, *num] = args
    if id_a not in dota_id_dict.keys():
        SessionLogger.info("[COMP]未添加用户 " + id_a)
        return [Plain(text="未添加用户 " + id_a + " ！")]
    elif id_b not in dota_id_dict.keys():
        SessionLogger.info("[COMP]未添加用户 " + id_b)
        return [Plain(text="未添加用户 " + id_b + " ！")]
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
        msg = [Plain(text=res)]
        SessionLogger.info("[COMP]返回成功")
        return msg


@args_parser(1, 0)
async def winrate_handler(*args, sender, event_type):
    '''最近胜率图展示

    用法: /winrate 或 /winrate id (num)'''
    if len(args) < 1 or len(args) > 2:
        return [Plain(text="缺少参数或参数过多")]
    query_id, *num = args
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


@args_parser(2, 0)
async def setdota_handler(*args, sender, event_type):
    '''设置用户对应的dota id

    用法: /setdota 昵称 id'''
    dota_id_dict[args[0]] = args[1]
    updateJSON(dota_dict_path, dota_id_dict)
    return [Plain(text="添加成功！")]


@args_parser(2, 0)
async def winrate_compare_handler(*args, sender, event_type):
    '''玩家间最近胜率数据对比

    用法: /wrcp id_b 或 /wrcp id_a id_b (num)'''
    args = list(args)
    if len(args) < 2:
        return [Plain(text="缺少参数或参数过多")]
    try:
        num = int(args[-1])
        ids = args[:len(args)-1]
    except:
        num = 0
        ids = list(args)
    for no, i in enumerate(ids):
        if i not in dota_id_dict.keys():
            SessionLogger.info("[WRCP]未添加用户 " + i)
            return [Plain(text="未添加用户 " + i + " ！")]
        ids[no] = dota_id_dict[i]
    else:
        if num <= 0 or num > 50:
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


@args_parser(2, 0)
async def star_compare_handler(*args, sender, event_type):
    '''玩家间最近五星图对比

    用法: /stcp id_b 或 /stcp id_a id_b (num)'''
    args = list(args)
    if len(args) < 2 or len(args) > 3:
        return [Plain(text="缺少参数或参数过多")]
    try:
        num = int(args[-1])
        ids = args[:len(args)-1]
    except:
        num = 0
        ids = list(args)
    for no, i in enumerate(ids):
        if i not in dota_id_dict.keys():
            SessionLogger.info("[STCP]未添加用户 " + i)
            return [Plain(text="未添加用户 " + i + " ！")]
        ids[no] = dota_id_dict[i]
    else:
        if num <= 0 or num > 50:
            num = 20
        pic_name, player_name_a, _ = getCompStarStat(ids[0], ids[1], num)
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


async def dotanews_handler(*args, sender, event_type):
    '''DOTA新闻订阅

    用法: /dotanews'''
    news_dict = readJSON(NEWS_JSON_PATH)
    if event_type == "GroupMessage" and groupToStr(sender.group) not in news_dict["member"]:
        news_dict["member"].append(groupToStr(sender.group))
    if event_type == "FriendMessage" and sender.id not in news_dict["member"]:
        news_dict["member"].append(sender.id)
    updateJSON(NEWS_JSON_PATH, news_dict)
    msg = [Plain(text="已订阅DOTA新闻\n")]
    SessionLogger.info("[DOTANEWS]返回成功")
    return msg


async def rmdotanews_handler(*args, sender, event_type):
    '''DOTA新闻取消订阅

    用法: /rmdotanews'''
    news_dict = readJSON(NEWS_JSON_PATH)
    if event_type == "GroupMessage" and groupToStr(sender.group) in news_dict["member"]:
        news_dict["member"].remove(groupToStr(sender.group))
    elif event_type == "FriendMessage" and sender.id in news_dict["member"]:
        news_dict["member"].remove(sender.id)
    if len(news_dict["member"])==0:
        del news_dict["member"]
    updateJSON(NEWS_JSON_PATH, news_dict)
    msg = [Plain(text="已取消订阅DOTA新闻\n")]
    SessionLogger.info("[RMDOTANEWS]返回成功")
    return msg


@args_parser(2,0)
async def hero_handler(*args, sender, event_type):
    '''展示玩家英雄平均数据

    用法: /hero (id) 英雄名'''
    if len(args) != 2:
        return [Plain(text="缺少参数或参数过多")]
    query_id = args[0]
    if query_id not in dota_id_dict.keys():
        SessionLogger.info("[HERO]未添加该用户")
        return [Plain(text="未添加该用户！")]
    else:
        query_id = dota_id_dict[query_id]
        res = getDotaHero(query_id, args[1])
        if type(res) == tuple:
            res = res[1]
            SessionLogger.info("[HERO]返回成功")
        elif res == 0:
            res = f"参数有误:{args[1]}"
            SessionLogger.info(f"[HERO]参数有误:{args[1]}")
        else:
            SessionLogger.info("[HERO]返回成功")
        return [Plain(text=res)]

@api_cache(2*60)
async def story_handler(*args,sender,event_type):
    '''dota战报展示

    用法: /story 比赛id'''
    if len(args) != 1:
        return [Plain(text="缺少参数或参数过多")]
    match_id = args[0]
    path = await getDotaStory(match_id)
    msg = []
    if type(path) != str:
        if path == 404:
            msg = [Plain(text=f"未找到比赛:{match_id}")]
            SessionLogger.info(f"[STORY]未找到比赛:{match_id}")
        elif path == 1:
            msg = [Plain(text=f"比赛{match_id}解析中，请等待2min后重试")]
            SessionLogger.info(f"[STORY]解析中:{match_id}")
    else:
        msg = [Image.fromFileSystem(path)]
        SessionLogger.info("[STORY]返回成功")
    return msg

@sub_app.subroutine
@schedule_task(name="DOTA更新订阅",interval=300)
async def news(app: Mirai):
    news_dict = readJSON(NEWS_JSON_PATH, defaultValue={"member": []})
    news = getDotaNews()
    if len(news) > 0:
        msg = []
        for i in news:
            img = []
            res = f"\n{i['title']}\n"
            if "[img]" in i["contents"]:
                pattern = r"\[img\][\S]*\[/img\]"
                imgs = re.findall(pattern, i["contents"])
                img.append(await Image.fromRemote(imgs[0][5:-6]))
                for to_rm in imgs:
                    i["contents"] = i["contents"].replace(to_rm, "")
                res += i["contents"].strip() + "\n\n"
            msg += img
            msg.append(Plain(text=res))
        try:
            for member in news_dict["member"]:
                if type(member)==str:
                    await app.sendGroupMessage(groupFromStr(member),msg)
                else:
                    await app.sendFriendMessage(member,msg)
        except exceptions.BotMutedError:
            pass


COMMANDS = {
                "dota": dota_handler, "winrate": winrate_handler,
                "stat": stat_handler, "setdota": setdota_handler,
                "comp": compare_handler, "wrcp": winrate_compare_handler,
                "star": star_handler, "stcp": star_compare_handler,
                "dotanews": dotanews_handler, "rmdotanews": rmdotanews_handler,
                "hero": hero_handler, "story":story_handler
            }
