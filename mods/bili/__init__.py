#encoding=Utf-8
from mirai import Mirai, Permission, Group, GroupMessage, MessageChain, Member, Plain, Image, Face, AtAll, At,FlashImage, exceptions
from mirai.logger import Session as SessionLogger
from urllib.request import urlretrieve
from pathlib import Path
from .dance_top import getTop3DanceToday, getRecommendDance
from .live import getLiveInfo, readMonitorDict, updateMonitorDict
from .._utils.convert import groupFromStr, groupToStr
import time
import asyncio

COMMANDS_FLAG = False

sub_app = Mirai(f"mirai://localhost:8080/?authKey=0&qq=0")

@sub_app.receiver("GroupMessage")
async def bili_handler(app: Mirai, group:Group, message:MessageChain, member:Member):
    sender=member.id
    groupId=group.id
    if message.toString()[:6] == "/dance":
        SessionLogger.info("[DANCE]来自群%d中成员%d的消息:" % (groupId,sender) + message.toString())
        title, author, pic, url = getTop3DanceToday()
        msg = [Plain(text="B站舞蹈区实时排名前3（已剔除潜在不适内容）\n")]
        for i, ti in enumerate(title):
            msg.append(Plain(text=str(i + 1) + "：" + ti + " by " + author[i] + "\n"))
            msg.append(Plain(text=url[i] + "\n"))
            img_path = str(Path(__file__).parent.joinpath('dance_' + str(i) + ".jpg"))
            urlretrieve(pic[i], img_path)
            msg.append(Image.fromFileSystem(img_path))
            msg.append(Plain(text="\n"))
        SessionLogger.info("[DANCE]返回成功")
        try:
            await app.sendGroupMessage(group,msg)
        except exceptions.BotMutedError:
            pass

    elif message.toString()[:10] == "/recommend":
        SessionLogger.info("[RECOM]来自群%d中成员%d的消息:" % (groupId,sender) + message.toString())
        title, author, pic, url = getRecommendDance()
        msg = [Plain(text="本次核心推荐up随机视频：\n")]
        for i, ti in enumerate(title):
            msg.append(Plain(text=str(i + 1) + "：" + ti + " by " + author[i] + "\n"))
            msg.append(Plain(text=url[i] + "\n"))
            img_path = str(Path(__file__).parent.joinpath('dance_' + str(i) + ".jpg"))
            urlretrieve(pic[i], img_path)
            msg.append(Image.fromFileSystem(img_path))
            msg.append(Plain(text="\n"))
        SessionLogger.info("[RECOM]返回成功")
        try:
            await app.sendGroupMessage(group,msg)
        except exceptions.BotMutedError:
            pass

    elif message.toString()[:5] == "/live":
        SessionLogger.info("[LIVE]来自群%d中成员%d的消息:" % (groupId,sender) + message.toString())
        room_id = message.toString()[6:]
        res = getLiveInfo(room_id)
        if res=="error":
            msg = [Plain(text="未找到该直播！")]
            SessionLogger.info("[LIVE]未找到该直播")
        else:
            monitor_dict = readMonitorDict()
            if room_id in monitor_dict.keys():
                if groupToStr(group) not in monitor_dict[room_id]:
                    monitor_dict[room_id].append(groupToStr(group))
            else:
                monitor_dict[room_id] = [groupToStr(group)]
            updateMonitorDict(monitor_dict)
            if res['isLive']==0:
                msg = [Plain(text="已加入监视列表\n" + res['name'] + " 未在直播.")]
            else:
                msg = [
                    Plain(text="已加入监视列表\n" + res['name'] + " 正在直播 " + "[{}]{}\n{}".format(res["area_name"],res["title"],res["url"])),
                    await Image.fromRemote(res["keyframe"])
                ]
            SessionLogger.info("[LIVE]返回成功")
        try:
            await app.sendGroupMessage(group,msg)
        except exceptions.BotMutedError:
            pass
    
    elif message.toString()[:7] == "/rmlive":
        SessionLogger.info("[LIVE]来自群%d中成员%d的消息:" % (groupId,sender) + message.toString())
        room_id = message.toString()[8:]
        res = getLiveInfo(room_id)
        if res=="error":
            msg = [Plain(text="未找到该直播！")]
            SessionLogger.info("[LIVE]未找到该直播")
        else:
            monitor_dict = readMonitorDict()
            if room_id in monitor_dict.keys():
                monitor_dict[room_id].remove(groupToStr(group))
            updateMonitorDict(monitor_dict)
            msg = [Plain(text="已将 {} 移出监视列表\n".format(res['name']))]
            SessionLogger.info("[LIVE]返回成功")
        try:
            await app.sendGroupMessage(group,msg)
        except exceptions.BotMutedError:
            pass

@sub_app.subroutine
async def monitor(app: Mirai):
    while 1:
        monitor_dict = readMonitorDict()
        for room_id in monitor_dict.keys():
            res = getLiveInfo(room_id)
            if res['isLive']==1 and time.time()+5*60*60-int(time.mktime(time.strptime(res['live_time'], "%Y-%m-%d %H:%M:%S")))<3*60:
                msg = [
                    Plain(text=res['name'] + " 开播啦! " + "[{}]{}\n{}".format(res["area_name"],res["title"],res["url"])),
                    await Image.fromRemote(res["keyframe"])
                ]
                try:
                    for group in monitor_dict[room_id]:
                        await app.sendGroupMessage(groupFromStr(group),msg)
                except exceptions.BotMutedError:
                    pass
        await asyncio.sleep(3*60)