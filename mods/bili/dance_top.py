from urllib import request
from pathlib import Path
import json
import random
from .cover_checker import detectSafeSearchUri

black_lists = ["男"]
up_lists = ["15385187", "84465926", "632887", "2689967", "5276",
            "8366990", "7375428", "466272", "13346799", "8581342"]

black_ups = ["399752044", "10139490", "643928765", "348470", "32782335"]

dance_api = "http://api.bilibili.com/x/web-interface/ranking?rid=129&day=1"
video_pri = "https://www.bilibili.com/video/"


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
    racy = []
    for _ in range(0, 3):
        rand_user = up_lists[random.randint(0, len(up_lists) - 1)]
        cur_url = "http://api.bilibili.com/x/space/arc/search?mid=" + rand_user + "&pn=1&ps=10&tid=129"
        try:
            html = request.urlopen(cur_url)
        except:
            return -1
        data = json.loads(html.read().decode('utf-8'))
        dance_list = data["data"]["list"]["vlist"]
        rand_dance = dance_list[random.randint(0, len(dance_list) - 1)]

        cover_url = "http:" + rand_dance["pic"]
        this_racy = detectSafeSearchUri(cover_url)
        bvid = rand_dance["bvid"]
        url.append(video_pri + bvid)
        author.append(rand_dance["author"])
        title.append(rand_dance["title"])
        pic.append(cover_url)
        racy.append(this_racy)
    return title, author, pic, url, racy


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
    racy = []
    for _, data in enumerate(dance_data["data"]["list"]):
        if checkTitle(data["title"]) == -1:
            continue
        u_id = data["mid"]
        if str(u_id) in black_ups:
            continue
        count += 1
        cover_url = data["pic"]
        this_racy = detectSafeSearchUri(cover_url)
        bvid = data["bvid"]
        url.append(video_pri + bvid)
        author.append(data["author"])
        title.append(data["title"])
        pic.append(cover_url)
        racy.append(this_racy)
        if count > 3:
            break
    return title, author, pic, url, racy
