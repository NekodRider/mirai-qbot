from urllib import request
from pathlib import Path
import json
import random

black_lists = ["男"]
up_lists = ["15385187", "84465926", "632887", "2689967", "5276"
            "8366990", "7375428", "466272", "13346799", "8581342"]

dance_api = "http://api.bilibili.com/x/web-interface/ranking?rid=129&day=1"
video_pri = "https://www.bilibili.com/video/"


def getDanceUrl(uid):
    return "http://api.bilibili.com/x/space/arc/search?mid=" + uid + "&pn=1&ps=10&tid=129"


def checkTitle(title):
    for word in black_lists:
        if word in title:
            return -1
    return 0


def getRecommendDance():
    author = []
    title = []
    pic = []
    url = []
    for i in range(0, 3):
        rand_user = up_lists[random.randint % len(up_lists)]
        url = getDanceUrl(rand_user)
        try:
            html = request.urlopen(url)
        except:
            return -1
        data = json.loads(html.read().decode('utf-8'))
        dance_list = data["data"]["list"]["vlist"]
        rand_dance = dance_list[random.randint % len(dance_list)]
        bvid = rand_dance["bvid"]
        url.append(video_pri + bvid)
        author.append(rand_dance["author"])
        title.append(rand_dance["title"])
        pic.append("http:" + rand_dance["pic"])
    return title, author, pic, url


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
