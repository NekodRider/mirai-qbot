from urllib import request
from pathlib import Path
import json

black_lists = ["男"]

dance_api = "http://api.bilibili.com/x/web-interface/ranking?rid=129&day=1"
video_pri = "https://www.bilibili.com/video/"


def checkTitle(title):
    for word in black_lists:
        if word in title:
            return -1
    return 0


def getTop3DanceToday():
    try:
        html = request.urlopen(dance_api)
    except:
        return -1
    count = 0
    dance_data = json.loads(html.read().decode('utf-8'))
    author = []
    title = []
    pic = []
    url = []
    for i, data in enumerate(dance_data["data"]["list"]):
        cur_dance = dance_data["data"]["list"][i]
        if checkTitle(cur_dance["title"]) == -1:
            continue
        count += 1
        bvid = cur_dance["bvid"]
        url.append(video_pri + bvid)
        author.append(cur_dance["author"])
        title.append(cur_dance["title"])
        pic.append(cur_dance["pic"])
        if count >= 3:
            break
    return title, author, pic, url
