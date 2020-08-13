#encoding=Utf-8
from mirai import Mirai, Permission, Group, GroupMessage, MessageChain, Member, Plain, Image, Face, AtAll, At,FlashImage, exceptions
from mirai.logger import Session as SessionLogger
from urllib.request import urlretrieve
from pathlib import Path
from .dance_top import getTop3DanceToday, getRecommendDance
from .live import getLiveInfo, getNameByUid
from .card import getCards
from .._utils import groupFromStr, groupToStr, readJSON, updateJSON
import time
import asyncio

BILI_LIVE_JSON_PATH = Path(__file__).parent.joinpath("bili_roomid.json")
BILI_UP_JSON_PATH = Path(__file__).parent.joinpath("bili_upid.json")
sub_app = Mirai(f"mirai://localhost:8080/?authKey=0&qq=0")

async def dance_handler(*args,sender,event_type):
    title, author, pic, url = getTop3DanceToday()
    msg = [Plain(text="B站舞蹈区实时排名前3（已剔除潜在不适内容）\n")]
    for i, ti in enumerate(title):
        msg.append(Plain(text=str(i + 1) + "：" + ti + " by " + author[i] + "\n"))
        msg.append(Plain(text=url[i] + "\n"))
        msg.append(await Image.fromRemote(pic[i]))
        msg.append(Plain(text="\n"))
    SessionLogger.info("[DANCE]返回成功")
    return msg

async def recommend_handler(*args,sender,event_type):
    title, author, pic, url = getRecommendDance()
    msg = [Plain(text="本次核心推荐up随机视频：\n")]
    for i, ti in enumerate(title):
        msg.append(Plain(text=str(i + 1) + "：" + ti + " by " + author[i] + "\n"))
        msg.append(Plain(text=url[i] + "\n"))
        msg.append(await Image.fromRemote(pic[i]))
        msg.append(Plain(text="\n"))
    SessionLogger.info("[RECOMMEND]返回成功")
    return msg

async def live_handler(*args,sender,event_type):
    if len(args)==0:
        msg = []
        monitor_dict = readJSON(BILI_LIVE_JSON_PATH)
        for room_id, target in monitor_dict.items():
            if (event_type=="GroupMessage" and groupToStr(sender.group) in target) \
                or (event_type=="FriendMessage" and sender.id in target):
                res = getLiveInfo(room_id)
                if res['isLive']==0:
                    msg.append(Plain(text=res['name'] + " 未在直播.\n"))
                else:
                    msg.append(Plain(text=res['name'] + " 正在直播 " + "[{}]{}\n{}".format(res["area_name"],res["title"],res["url"])))
                    msg.append(await Image.fromRemote(res["keyframe"]))
        return msg

    room_id = args[0]
    res = getLiveInfo(room_id)
    if res=="error":
        msg = [Plain(text="未找到该直播！")]
        SessionLogger.info("[LIVE]未找到该直播")
    else:
        monitor_dict = readJSON(BILI_LIVE_JSON_PATH)
        if room_id in monitor_dict.keys():
            if event_type=="GroupMessage" and groupToStr(sender.group) not in monitor_dict[room_id]:
                monitor_dict[room_id].append(groupToStr(sender.group))
            if event_type=="FriendMessage" and sender.id not in monitor_dict[room_id]:
                monitor_dict[room_id].append(sender.id)
        else:
            if event_type=="GroupMessage":
                monitor_dict[room_id] = [groupToStr(sender.group)]
            elif event_type=="FriendMessage":
                monitor_dict[room_id] = [sender.id]
        updateJSON(BILI_LIVE_JSON_PATH,monitor_dict)
        if res['isLive']==0:
            msg = [Plain(text="已加入监视列表\n" + res['name'] + " 未在直播.")]
        else:
            msg = [
                Plain(text="已加入监视列表\n" + res['name'] + " 正在直播 " + "[{}]{}\n{}".format(res["area_name"],res["title"],res["url"])),
                await Image.fromRemote(res["keyframe"])
            ]
        SessionLogger.info("[LIVE]返回成功")
    return msg

async def rmlive_handler(*args,sender,event_type):
    if len(args)!=1:
        return [Plain(text="缺少参数或参数过多")]
    room_id = args[0]
    res = getLiveInfo(room_id)
    if res=="error":
        msg = [Plain(text="未找到该直播！")]
        SessionLogger.info("[LIVE]未找到该直播")
    else:
        monitor_dict = readJSON(BILI_LIVE_JSON_PATH)
        if room_id in monitor_dict.keys():
            if event_type=="GroupMessage":
                monitor_dict[room_id].remove(groupToStr(sender.group))
            elif event_type=="FriendMessage":
                monitor_dict[room_id].remove(sender.id)
        updateJSON(BILI_LIVE_JSON_PATH,monitor_dict)
        msg = [Plain(text="已将 {} 移出监视列表\n".format(res['name']))]
        SessionLogger.info("[LIVE]返回成功")
    return msg

async def up_handler(*args,sender,event_type):
    if len(args)==0:
        res = "目前关注的UP主有：\n"
        up_dict = readJSON(BILI_UP_JSON_PATH)
        for up, target in up_dict.items():
            if (event_type=="GroupMessage" and groupToStr(sender.group) in target) \
                or (event_type=="FriendMessage" and sender.id in target):
                res += getNameByUid(up) + " "
        return [Plain(text=res)]

    up_id = args[0]
    up_name = getNameByUid(up_id)
    res = getCards(up_id)
    if res=="error":
        msg = [Plain(text="未找到该UP主！")]
        SessionLogger.info("[UP]未找到该UP主")
    else:
        up_dict = readJSON(BILI_UP_JSON_PATH)
        if up_id in up_dict.keys():
            if event_type=="GroupMessage" and groupToStr(sender.group) not in up_dict[up_id]:
                up_dict[up_id].append(groupToStr(sender.group))
            if event_type=="FriendMessage" and sender.id not in up_dict[up_id]:
                up_dict[up_id].append(sender.id)
        else:
            if event_type=="GroupMessage":
                up_dict[up_id] = [groupToStr(sender.group)]
            elif event_type=="FriendMessage":
                up_dict[up_id] = [sender.id]
        updateJSON(BILI_UP_JSON_PATH,up_dict)
        if len(res)==0:
            msg = [Plain(text="已加入关注列表 " + up_name + " 暂无新投稿.")]
        else:
            msg = [Plain(text=f"已加入关注列表 {up_name}\n")]
            for i in res:
                msg.append(Plain(text=f"{up_name} 投稿了视频《{i['title']}》:{i['url']}\n"))
                msg.append(await Image.fromRemote(i["pic"]))
                msg.append(Plain(text="\n"))
        SessionLogger.info("[LIVE]返回成功")
    return msg

async def rmup_handler(*args,sender,event_type):
    if len(args)!=1:
        return [Plain(text="缺少参数或参数过多")]
    up_id = args[0]
    res = getCards(up_id)
    if res=="error":
        msg = [Plain(text="未找到该UP主！")]
        SessionLogger.info("[RMUP]未找到该UP主")
    else:
        up_dict = readJSON(BILI_UP_JSON_PATH)
        if up_id in up_dict.keys():
            if event_type=="GroupMessage":
                up_dict[up_id].remove(groupToStr(sender.group))
            elif event_type=="FriendMessage":
                up_dict[up_id].remove(sender.id)
        updateJSON(BILI_UP_JSON_PATH,up_dict)
        msg = [Plain(text="已将 {} 移出监视列表\n".format(getNameByUid(up_id)))]
        SessionLogger.info("[RMUP]返回成功")
    return msg

@sub_app.subroutine
async def live_monitor(app: Mirai):
    while 1:
        monitor_dict = readJSON(BILI_LIVE_JSON_PATH,defaultValue={"time":time.time()})
        if time.time() - monitor_dict["time"] >= 3*60:
            for room_id in monitor_dict.keys():
                res = getLiveInfo(room_id)
                if res['isLive']==1 and time.time()+5*60*60-int(time.mktime(time.strptime(res['live_time'], "%Y-%m-%d %H:%M:%S")))<3*60:
                    msg = [
                        Plain(text=res['name'] + " 开播啦! " + "[{}]{}\n{}".format(res["area_name"],res["title"],res["url"])),
                        await Image.fromRemote(res["keyframe"])
                    ]
                    try:
                        for member in monitor_dict[room_id]:
                            if type(member)==str:
                                await app.sendGroupMessage(groupFromStr(member),msg)
                            else:
                                await app.sendFriendMessage(member,msg)
                    except exceptions.BotMutedError:
                        pass
            monitor_dict["time"] = time.time()
            updateJSON(BILI_LIVE_JSON_PATH,monitor_dict)
        await asyncio.sleep(3*60)

@sub_app.subroutine
async def up_monitor(app: Mirai):
    while 1:
        up_dict = readJSON(BILI_UP_JSON_PATH,defaultValue={"time":time.time()})
        if time.time() - up_dict["time"] >= 60*60:
            for up_id in up_dict.keys():
                res = getCards(up_id)
                up_name = getNameByUid(up_id)
                if len(res)!=0:
                    msg = []
                    for i in res:
                        msg.append(Plain(text=f"{up_name} 投稿了视频《{i['title']}》:{i['url']}\n"))
                        msg.append(await Image.fromRemote(i["pic"]))
                        msg.append(Plain(text="\n"))
                    try:
                        for member in up_dict[up_id]:
                            if type(member)==str:
                                await app.sendGroupMessage(groupFromStr(member),msg)
                            else:
                                await app.sendFriendMessage(member,msg)
                    except exceptions.BotMutedError:
                        pass
            up_dict["time"] = time.time()
            updateJSON(BILI_UP_JSON_PATH,up_dict)
        await asyncio.sleep(60*60)

COMMANDS = {"dance":dance_handler,"recommend":recommend_handler,"live":live_handler,"rmlive":rmlive_handler,
            "up":up_handler,"rmup":rmup_handler}
