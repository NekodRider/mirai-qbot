import json
from urllib import request

from bot import defaultLogger as logger

from .api import live_api, user_api


def getNameByUid(uid):
    url = user_api.format(uid)
    try:
        html = request.urlopen(url)
    except Exception as e:
        logger.exception(e)
        raise
    data = json.loads(html.read().decode('utf-8'))
    if data["code"] != 0:
        return f"未找到用户 {uid}."
    return data["data"]["name"]


def getLiveInfo(room_id):
    url = live_api.format(room_id)
    try:
        html = request.urlopen(url)
    except Exception as e:
        logger.exception(e)
        raise
    live_data = json.loads(html.read().decode('utf-8'))
    if live_data["code"] != 0:
        return f"未找到房间 {room_id}."
    uid = live_data["data"]["uid"]
    res = {}
    res['isLive'] = live_data["data"]["live_status"]
    res['title'] = live_data["data"]["title"]
    res['keyframe'] = live_data["data"]["keyframe"]
    res['area_name'] = live_data["data"]["area_name"]
    res['url'] = "https://live.bilibili.com/" + room_id
    res['live_time'] = live_data["data"]["live_time"]
    res['name'] = getNameByUid(uid)

    return res
