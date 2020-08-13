from urllib import request
from pathlib import Path
import json

def readMonitorDict():
    with open(Path(__file__).parent.joinpath("bili_roomid.json"),encoding='utf-8') as f:
        d = json.loads(f.read())
    return d

def updateMonitorDict(d):
    with open(Path(__file__).parent.joinpath("bili_roomid.json"),'w',encoding='utf-8') as f:
        f.write(json.dumps(d))

def getLiveInfo(room_id):
    url = "https://api.live.bilibili.com/room/v1/Room/get_info?id=" + room_id
    html = request.urlopen(url)
    live_data = json.loads(html.read().decode('utf-8'))
    if live_data["code"]!=0:
        return "error"
    uid = live_data["data"]["uid"]
    res = {}
    res['isLive'] = live_data["data"]["live_status"]
    res['title'] = live_data["data"]["title"]
    res['keyframe'] = live_data["data"]["keyframe"]
    res['area_name'] = live_data["data"]["area_name"]
    res['url'] = "https://live.bilibili.com/" + room_id
    res['live_time'] = live_data["data"]["live_time"]
    url = "https://api.bilibili.com/x/space/acc/info?mid=" + str(uid)
    html = request.urlopen(url)
    live_data = json.loads(html.read().decode('utf-8'))
    res['name'] = live_data["data"]["name"]

    return res
