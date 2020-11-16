from urllib import request
import json
import time

from bot import defaultLogger as logger
from .api import video_api, card_api


def getCards(uid, timeout=600):
    try:
        html = request.urlopen(card_api.format(uid))
    except Exception as e:
        logger.exception(e)
        raise
    data = json.loads(html.read().decode('utf-8'))
    if data["code"] != 0:
        return "error"
    cards = data["data"]["cards"]

    res = []
    for card in cards:
        if card["desc"]["type"] != 8:
            continue
        if time.time() - card["desc"]["timestamp"] > timeout or time.time(
        ) < card["desc"]["timestamp"]:
            break
        tmp = {}
        card_info = json.loads(card["card"])
        tmp["title"] = card_info["title"]
        tmp["pic"] = card_info["pic"]
        tmp["url"] = video_api.format(card["desc"]["bvid"])
        res.append(tmp)
    return res
