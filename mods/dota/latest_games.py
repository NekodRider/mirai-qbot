from .helper import getDotaPlayerInfo, getDotaGamesInfo, error_codes
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def getLatestWinningStat(playerId, total=20):
    res = {}
    player_data = getDotaPlayerInfo(playerId, "/summary")
    if type(player_data) == type(""):
        return error_codes[player_data]
    games_data = getDotaGamesInfo(playerId, "?take=" + str(total) + "&include=Player")

    player_name = games_data[0]["players"][0]["steamAccount"]["name"]
    for id, match in enumerate(games_data):
        res['isVic'] = (1 if match["players"][0]["isVictory"] else 0) + res.get('isVic', 0)
        res['k'] = int(match["players"][0]["numKills"]) + res.get('k', 0)
        res['d'] = int(match["players"][0]["numDeaths"]) + res.get('d', 0)
        res['a'] = int(match["players"][0]["numAssists"]) + res.get('a', 0)
        res['net'] = int(match["players"][0]["networth"]) + res.get('net', 0)
        res['exp'] = int(int(match["players"][0]["experiencePerMinute"]) * (int(match["durationSeconds"]) / 60)) + res.get('net', 0)
        res['last'] = int(match["players"][0]["numLastHits"]) + res.get('last', 0)
        res['deny'] = int(match["players"][0]["numDenies"]) + res.get('deny', 0)
        res['dmg'] = int(match["players"][0]["heroDamage"]) + res.get('dmg', 0)
        res['tow'] = int(match["players"][0]["towerDamage"]) + res.get('tow', 0)
        res['heal'] = int(match["players"][0]["heroHealing"]) + res.get('heal', 0)
    reports = list(map(lambda value: round(value / total, 2), res.values()))
    kda = round((res['k'] + res['a']) / (res['d'] if res['d'] != 0 else 1), 2)

    res = player_name + '最近' + str(total) + '游戏总数据统计如下：\n'
    res += '胜率：' + str(reports[0]) + '\n'
    res += 'KDA：' + str(kda) + '\n'
    res += '场均击杀：' + str(reports[1]) + '\n'
    res += '场均死亡：' + str(reports[2]) + '\n'
    res += '场均助攻：' + str(reports[3]) + '\n'
    res += '场均GPM：' + str(reports[4]) + '\n'
    res += '场均XPM：' + str(reports[5]) + '\n'
    res += '场均正补：' + str(reports[6]) + '\n'
    res += '场均反补：' + str(reports[7]) + '\n'
    res += '场均伤害：' + str(reports[8]) + '\n'
    res += '场均建筑伤害：' + str(reports[9]) + '\n'
    res += '场均治疗：' + str(reports[10]) + '\n'
    return res
