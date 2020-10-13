# encoding=Utf-8
import time
import typing as T
from graia.application.group import Member
from graia.application.friend import Friend
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain, Image
from pathlib import Path

from .dance import getTop3DanceToday, getRecommendDance
from .live import getLiveInfo, getNameByUid
from .card import getCards
from bot import Bot
from bot.logger import defaultLogger as logger
from mods._utils.storage import readJSON, updateJSON
from mods._utils.convert import groupToStr, groupFromStr

BILI_LIVE_JSON_PATH = Path(__file__).parent.joinpath("bili_roomid.json")
BILI_UP_JSON_PATH = Path(__file__).parent.joinpath("bili_upid.json")
RACY_LIST = ["🌚🌚🌚🌚🌝", "🌚🌚🌚🌝🌝", "🌚🌚🌝🌝🌝", "🌚🌝🌝🌝🌝", "🌝🌝🌝🌝🌝", "Google 晕了Orz"]


async def dance_handler(*args, subject: T.Union[Member, Friend]):
    '''B站舞蹈区排行

    用法: /dance'''
    title, author, pic, url, racy = getTop3DanceToday()
    msg = [Plain("B站舞蹈区实时排名前3（已剔除潜在不适内容）\n")]
    for i, ti in enumerate(title):
        msg.append(Plain(str(i + 1) + "：" + ti + " by " + author[i] + "\n"))
        msg.append(Plain(url[i] + "\n"))
        msg.append(Plain("se指数（by Google）：" + RACY_LIST[racy[i] - 1] + "\n"))
        msg.append(Image.fromNetworkAddress(pic[i]))
        msg.append(Plain("\n"))
    logger.info("[DANCE]返回成功")
    return MessageChain.create(msg)


async def recommend_handler(*args, subject: T.Union[Member, Friend]):
    '''td金牌推荐舞见视频

    用法: /recommend'''
    title, author, pic, url, racy = getRecommendDance()
    msg = [Plain(text="本次核心推荐up随机视频：\n")]
    for i, ti in enumerate(title):
        msg.append(Plain(str(i + 1) + "：" + ti + " by " + author[i] + "\n"))
        msg.append(Plain(url[i] + "\n"))
        msg.append(Plain("se指数（by Google）：" + RACY_LIST[racy[i] - 1] + "\n"))
        msg.append(Image.fromNetworkAddress(pic[i]))
        msg.append(Plain("\n"))
    logger.info("[RECOMMEND]返回成功")
    return MessageChain.create(msg)


async def live_handler(*args, subject: T.Union[Member, Friend]):
    '''B站直播间开播订阅

    用法: /live 房间号'''
    if len(args) == 0:
        msg = []
        monitor_dict = readJSON(BILI_LIVE_JSON_PATH)
        for room_id, target in monitor_dict.items():
            if room_id == "time":
                continue
            if (isinstance(subject, Member) and groupToStr(subject.group) in target) \
                    or (isinstance(subject, Friend) and subject.id in target):
                res = getLiveInfo(room_id)
                if res['isLive'] == 0:
                    msg.append(Plain(res['name'] + " 未在直播.\n"))
                else:
                    msg.append(
                        Plain(res['name'] + " 正在直播 " + "[{}]{}\n{}".format(
                            res["area_name"], res["title"], res["url"])))
                    msg.append(Image.fromNetworkAddress(res["keyframe"]))
        return MessageChain.create(msg)

    room_id = args[0]
    res = getLiveInfo(room_id)
    if res == "error":
        msg = [Plain("未找到该直播！")]
        logger.info("[LIVE]未找到该直播")
    else:
        monitor_dict = readJSON(BILI_LIVE_JSON_PATH)
        if room_id in monitor_dict.keys():
            if isinstance(subject, Member) and groupToStr(
                    subject.group) not in monitor_dict[room_id]:
                monitor_dict[room_id].append(groupToStr(subject.group))
            elif isinstance(subject,
                            Friend) and subject.id not in monitor_dict[room_id]:
                monitor_dict[room_id].append(subject.id)
        else:
            if isinstance(subject, Member):
                monitor_dict[room_id] = [groupToStr(subject.group)]
            elif isinstance(subject, Friend):
                monitor_dict[room_id] = [subject.id]
        updateJSON(BILI_LIVE_JSON_PATH, monitor_dict)
        if res['isLive'] == 0:
            msg = [Plain("已加入监视列表\n" + res['name'] + " 未在直播.")]
        else:
            msg = [
                Plain("已加入监视列表\n" +
                      res['name'] + " 正在直播 " + "[{}]{}\n{}".format(
                          res["area_name"], res["title"], res["url"])),
                Image.fromNetworkAddress(res["keyframe"])
            ]
        logger.info("[LIVE]返回成功")
    return MessageChain.create(msg)


async def rmlive_handler(*args, subject: T.Union[Member, Friend]):
    '''取消订阅直播间

    用法: /rmlive 房间号'''
    if len(args) != 1:
        return MessageChain.create([Plain("缺少参数或参数过多")])
    room_id = args[0]
    res = getLiveInfo(room_id)
    if res == "error":
        msg = [Plain("未找到该直播！")]
        logger.info("[RMLIVE]未找到该直播")
    else:
        monitor_dict = readJSON(BILI_LIVE_JSON_PATH)
        if room_id in monitor_dict.keys():
            if isinstance(subject, Member):
                monitor_dict[room_id].remove(groupToStr(subject.group))
            elif isinstance(subject, Friend):
                monitor_dict[room_id].remove(subject.id)
            if len(monitor_dict[room_id]) == 0:
                del monitor_dict[room_id]
        updateJSON(BILI_LIVE_JSON_PATH, monitor_dict)
        msg = [Plain("已将 {} 移出监视列表\n".format(res['name']))]
        logger.info("[RMLIVE]返回成功")
    return MessageChain.create(msg)


async def up_handler(*args, subject: T.Union[Member, Friend]):
    '''订阅UP主投稿

    用法: /up UP主uid'''
    if len(args) == 0:
        res = "目前关注的UP主有：\n"
        up_dict = readJSON(BILI_UP_JSON_PATH)
        for up, target in up_dict.items():
            if up == "time":
                continue
            if (isinstance(subject, Member) and groupToStr(subject.group) in target) \
                    or (isinstance(subject, Friend) and subject.id in target):
                res += getNameByUid(up) + " "
        return MessageChain.create([Plain(res)])

    up_id = args[0]
    up_name = getNameByUid(up_id)
    res = getCards(up_id)
    if res == "error":
        msg = [Plain("未找到该UP主！")]
        logger.info("[UP]未找到该UP主")
    else:
        up_dict = readJSON(BILI_UP_JSON_PATH)
        if up_id in up_dict.keys():
            if isinstance(subject, Member) and groupToStr(
                    subject.group) not in up_dict[up_id]:
                up_dict[up_id].append(groupToStr(subject.group))
            if isinstance(subject, Friend) and subject.id not in up_dict[up_id]:
                up_dict[up_id].append(subject.id)
        else:
            if isinstance(subject, Member):
                up_dict[up_id] = [groupToStr(subject.group)]
            elif isinstance(subject, Friend):
                up_dict[up_id] = [subject.id]
        updateJSON(BILI_UP_JSON_PATH, up_dict)
        if len(res) == 0:
            msg = [Plain("已加入关注列表 " + up_name + " 暂无新投稿.")]
        else:
            msg = [Plain(f"已加入关注列表 {up_name}\n")]
            for i in res:
                msg.append(Plain(f"{up_name} 投稿了视频《{i['title']}》:{i['url']}\n"))
                msg.append(Image.fromNetworkAddress(i["pic"]))
                msg.append(Plain("\n"))
        logger.info("[UP]返回成功")
    return MessageChain.create(msg)


async def rmup_handler(*args, subject: T.Union[Member, Friend]):
    '''取消订阅UP主投稿

    用法: /rmup UP主uid'''
    if len(args) != 1:
        return MessageChain.create([Plain("缺少参数或参数过多")])
    up_id = args[0]
    res = getCards(up_id)
    if res == "error":
        msg = [Plain("未找到该UP主！")]
        logger.info("[RMUP]未找到该UP主")
    else:
        up_dict = readJSON(BILI_UP_JSON_PATH)
        if up_id in up_dict.keys():
            if isinstance(subject, Member):
                up_dict[up_id].remove(groupToStr(subject.group))
            elif isinstance(subject, Friend):
                up_dict[up_id].remove(subject.id)
            if len(up_dict[up_id]) == 0:
                del up_dict[up_id]
        updateJSON(BILI_UP_JSON_PATH, up_dict)
        msg = [Plain("已将 {} 移出监视列表\n".format(getNameByUid(up_id)))]
        logger.info("[RMUP]返回成功")
    return MessageChain.create(msg)


async def live_scheduler(bot: Bot):
    monitor_dict = readJSON(BILI_LIVE_JSON_PATH, defaultValue={})
    for room_id in monitor_dict.keys():
        res = getLiveInfo(room_id)
        if res['isLive'] == 1 and time.time() - int(
                time.mktime(time.strptime(res['live_time'],
                                          "%Y-%m-%d %H:%M:%S"))) < 600:
            msg = MessageChain.create([
                Plain(res['name'] + " 开播啦! " + "[{}]{}\n{}".format(
                    res["area_name"], res["title"], res["url"])),
                Image.fromNetworkAddress(res["keyframe"])
            ])
            for member in monitor_dict[room_id]:
                if type(member) == str:
                    await bot.sendMessage(groupFromStr(member), msg)
                else:
                    await bot.sendMessage(member, msg)


async def up_scheduler(bot: Bot):
    up_dict = readJSON(BILI_UP_JSON_PATH, defaultValue={})
    for up_id in up_dict.keys():
        res = getCards(up_id)
        up_name = getNameByUid(up_id)
        if len(res) != 0:
            msg = []
            for i in res:
                msg.append(
                    Plain(text=f"{up_name} 投稿了视频《{i['title']}》:{i['url']}\n"))
                msg.append(Image.fromNetworkAddress(i["pic"]))
                msg.append(Plain(text="\n"))
            msg = MessageChain.create(msg)
            for member in up_dict[up_id]:
                if type(member) == str:
                    await bot.sendMessage(groupFromStr(member), msg)
                else:
                    await bot.sendMessage(member, msg)


COMMANDS = {
    "dance": dance_handler,
    "recommend": recommend_handler,
    "live": live_handler,
    "rmlive": rmlive_handler,
    "up": up_handler,
    "rmup": rmup_handler
}

SCHEDULES = {
    "B站直播订阅": {
        "func": live_scheduler,
        "interval": 600
    },
    "B站UP投稿订阅": {
        "func": up_scheduler,
        "interval": 600
    }
}
