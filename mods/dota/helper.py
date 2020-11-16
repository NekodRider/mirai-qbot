from urllib import request
from typing import Union
import json

from bot import defaultLogger as logger
from .constants import api_dict,hero_dict, hero_dict_en


def getDotaPlayerInfo(playerId, playerArgs="") -> Union[dict, None]:
    try:
        html = request.urlopen(api_dict["player"].format(playerId,playerArgs))
    except Exception as e:
        logger.exception(e)
        raise
    player_data = json.loads(html.read().decode("utf-8"))
    if playerArgs == "" and player_data["steamAccount"]["name"] == "Unknown":
        return None
    return player_data


def getDotaGamesInfo(playerId, matchesArgs=""):
    try:
        html = request.urlopen(api_dict["player_matches"].format(playerId,matchesArgs))
    except Exception as e:
        logger.exception(e)
        raise
    games_data = json.loads(html.read().decode("utf-8"))
    return games_data


def getDotaGamesInfoOpenDota(playerId):
    req = request.Request(api_dict["player_matches_opendota"].format(playerId))
    req.add_header("User-Agent", "Chrome/69.0.3497.81 Safari/537.36")
    try:
        html = request.urlopen(req)
    except Exception as e:
        logger.exception(e)
        raise
    games_data = json.loads(html.read().decode("utf-8"))
    return games_data


def getDotaHero(playerId, heroName):
    res = {}
    hero_id = -1
    for k, v in hero_dict.items():
        if v == heroName:
            res["hero"] = v
            hero_id = k
            break
    player_info = getDotaPlayerInfo(playerId)
    if hero_id == -1 or not player_info:
        return None
    res["name"] = player_info["steamAccount"]["name"]
    try:
        html = request.urlopen(api_dict["player_hero"])
    except Exception as e:
        logger.exception(e)
        raise
    txt = html.read().decode("utf-8")
    if txt == "":
        return f"{res['name']} 也配玩 {res['hero']}？"
    
    data = json.loads(txt)
    res["win_stat"] = f"{round(data['winCount']/data['matchCount']*100,2)}% - {data['winCount']}W/{data['matchCount']-data['winCount']}L"
    res["kda"] = f"{int(data['avgNumKills'])}/{int(data['avgNumDeaths'])}/{int(data['avgNumAssists'])}"
    res["gpm"] = int(data["avgGoldPerMinute"])

    def getLaneMatchCount(elem):
        return elem["laneMatchCount"]

    def getRoleLaneMatchCount(elem):
        return elem["lanes"][0]["laneMatchCount"]

    for role in data["position"]:
        role["lanes"].sort(key=getLaneMatchCount, reverse=True)

    data["position"].sort(key=getRoleLaneMatchCount, reverse=True)
    role = data["position"][0]

    res["role"] = f"在{round(role['lanes'][0]['laneMatchCount']/data['matchCount']*100,2)}%的比赛中担任"
    res["role"] += ("优势路" if role["lanes"][0]["laneType"] == 1 else
                    ("中路" if role["lanes"][0]["laneType"] == 2 else
                     ("游走" if role["lanes"][0]["laneType"] == 0 else "劣势路")))
    res["role"] += "核心" if role["roleType"] == 0 else "辅助"
    result = f"{res['name']} 使用 {res['hero']} {res['role']}\n胜率：{res['win_stat']}  KDA：{res['kda']}  GPM：{res['gpm']}"
    return result


def getNameDict(matchId):
    req = request.Request(api_dict["match"].format(matchId))
    req.add_header("User-Agent", "Chrome/69.0.3497.81 Safari/537.36")
    try:
        html = request.urlopen(req)
    except Exception as e:
        logger.exception(e)
        raise
    players_data = json.loads(html.read().decode("utf-8"))["players"]
    res = {}
    for p in players_data:
        if "personaname" in p.keys():
            res[hero_dict_en[str(p["hero_id"])]] = p["personaname"]
    return res
