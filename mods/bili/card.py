from urllib import request
import json
import time


def getCards(uid, timeout=600):
    url = "https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid=" + uid
    html = request.urlopen(url)
    data = json.loads(html.read().decode('utf-8'))
    if data["code"] != 0:
        return "error"
    cards = data["data"]["cards"]

    res = []
    for card in cards:
        if card["desc"]["type"] != 8:
            continue
        if time.time() - card["desc"]["timestamp"] > timeout:
            break
        tmp = {}
        card_info = json.loads(card["card"])
        tmp["title"] = card_info["title"]
        tmp["pic"] = card_info["pic"]
        tmp["url"] = "https://www.bilibili.com/video/" + card["desc"]["bvid"]
        res.append(tmp)
    return res
