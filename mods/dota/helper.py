from urllib import request
from pathlib import Path
import json
import time

from .constants import hero_dict, hero_dict_en

dota_dict_path = Path(__file__).parent.joinpath("dota_id.json")


def getDotaPlayerInfo(playerId, playerArgs=""):
    url = f"https://api.stratz.com/api/v1/Player/{playerId}{playerArgs}"
    try:
        html = request.urlopen(url)
    except:
        return "404_NOT_FOUND"
    player_data = json.loads(html.read().decode("utf-8"))
    if playerArgs == "" and player_data["steamAccount"]["name"] == "Unknown":
        return "NO_SUCH_PLAYER"
    return player_data


def getDotaGamesInfo(playerId, matchesArgs=""):
    url = "https://api.stratz.com/api/v1/Player/" + playerId + "/matches" + matchesArgs
    html = request.urlopen(url)
    games_data = json.loads(html.read().decode("utf-8"))
    return games_data


def getDotaGamesInfoOpenDota(playerId, matchesArgs=""):
    url = f"https://api.opendota.com/api/players/{playerId}/recentMatches"
    req = request.Request(url)
    req.add_header("User-Agent", "Chrome/69.0.3497.81 Safari/537.36")
    html = request.urlopen(req)
    games_data = json.loads(html.read().decode("utf-8"))
    return games_data


def steam_html_process(raw_str):
    left = 0
    while 1:
        l = raw_str[left:].find("[")
        if l == -1:
            break
        elif "img" != raw_str[left + l + 1:left + l + 4]:
            r = raw_str[left:].find("]")
            raw_str = raw_str[:left + l] + raw_str[left + r + 1:]
            left = left + l
        else:
            r = raw_str[left:].find("]")
            r = raw_str[left + r + 1:].find("]")
            left = left + r + 1
    return raw_str


def getDotaNews(timeout=300):
    url = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=570&feeds=steam_community_announcements,steam_updates&count=1"
    html = request.urlopen(url)
    news_list = json.loads(html.read().decode("utf-8"))["appnews"]["newsitems"]
    now = time.time()
    ret = []
    for i in news_list:
        if now - i["date"] > timeout:
            break
        tmp = {}
        tmp["title"] = i["title"]
        tmp["url"] = i["url"]
        tmp["contents"] = steam_html_process(i["contents"])
        ret.append(tmp)
    return ret


def getDotaHero(playerId, heroName):
    res = {}
    hero_id = -1
    for k, v in hero_dict.items():
        if v == heroName:
            res["hero"] = v
            hero_id = k
            break
    if hero_id == -1:
        return 0
    res["name"] = getDotaPlayerInfo(playerId)["steamAccount"]["name"]
    url = f"https://api.stratz.com/api/v1/Player/{playerId}/heroPerformance/{hero_id}?gameMode=1,2,3,4"
    html = request.urlopen(url)
    txt = html.read().decode("utf-8")
    if txt == "":
        return (0, f"{res['name']} 也配玩 {res['hero']}？")
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
    url = f"https://api.opendota.com/api/matches/{matchId}"
    req = request.Request(url)
    req.add_header("User-Agent", "Chrome/69.0.3497.81 Safari/537.36")
    html = request.urlopen(req)
    players_data = json.loads(html.read().decode("utf-8"))["players"]
    res = {}
    for p in players_data:
        if "personaname" in p.keys():
            res[hero_dict_en[str(p["hero_id"])]] = p["personaname"]
    return res
