from urllib import request
import json


def getNameByUid(uid):
    url = "https://api.bilibili.com/x/space/acc/info?mid=" + str(uid)
    html = request.urlopen(url)
    live_data = json.loads(html.read().decode('utf-8'))
    return live_data["data"]["name"]


def getLiveInfo(room_id):
    url = "https://api.live.bilibili.com/room/v1/Room/get_info?id=" + room_id
    html = request.urlopen(url)
    live_data = json.loads(html.read().decode('utf-8'))
    if live_data["code"] != 0:
        return "error"
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
