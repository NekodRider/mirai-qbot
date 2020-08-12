from .helper import getDotaPlayerInfo, getDotaGamesInfo, error_codes


def getLatestGamesStat(playerId, total):
    res = {}
    player_data = getDotaPlayerInfo(playerId, "/summary")
    if type(player_data) == type(""):
        return error_codes[player_data], 0, 0, 0, 0
    games_data = getDotaGamesInfo(playerId, "?take=" + str(total) + "&include=Player")

    player_name = games_data[0]["players"][0]["steamAccount"]["name"]
    total_time = 0
    exp = 0
    net = 0
    for id, match in enumerate(games_data):
        res['isVic'] = (1 if match["players"][0]["isVictory"] else 0) + res.get('isVic', 0)
        res['k'] = int(match["players"][0]["numKills"]) + res.get('k', 0)
        res['d'] = int(match["players"][0]["numDeaths"]) + res.get('d', 0)
        res['a'] = int(match["players"][0]["numAssists"]) + res.get('a', 0)
        res['last'] = int(match["players"][0]["numLastHits"]) + res.get('last', 0)
        res['deny'] = int(match["players"][0]["numDenies"]) + res.get('deny', 0)
        res['dmg'] = int(match["players"][0]["heroDamage"]) + res.get('dmg', 0)
        res['tow'] = int(match["players"][0]["towerDamage"]) + res.get('tow', 0)
        res['heal'] = int(match["players"][0]["heroHealing"]) + res.get('heal', 0)
        total_time += int(match["durationSeconds"])
        exp += int(int(match["players"][0]["experiencePerMinute"]) * (int(match["durationSeconds"]) / 60))
        net += int(int(match["players"][0]["goldPerMinute"]) * (int(match["durationSeconds"]) / 60))

    reports = list(map(lambda value: round(value / total, 2), res.values()))
    kda = round((res['k'] + res['a']) / (res['d'] if res['d'] != 0 else 1), 2)
    total_time /= 60
    gpm = round(net / total_time, 2)
    xpm = round(exp / total_time, 2)
    return reports, kda, gpm, xpm, player_name


def getLatestWinningStat(playerId, total=20):
    reports, kda, gpm, xpm, player_name = getLatestGamesStat(playerId, total)
    if type(reports) == type(""):
        return reports
    res = player_name + '最近' + str(total) + '游戏总数据统计如下：\n'
    res += '胜率：' + str(reports[0]) + '\n'
    res += 'KDA：' + str(kda) + '\n'
    res += '场均击杀：' + str(reports[1]) + '\n'
    res += '场均死亡：' + str(reports[2]) + '\n'
    res += '场均助攻：' + str(reports[3]) + '\n'
    res += '场均GPM：' + str(gpm) + '\n'
    res += '场均XPM：' + str(xpm) + '\n'
    res += '场均正补：' + str(reports[4]) + '\n'
    res += '场均反补：' + str(reports[5]) + '\n'
    res += '场均英雄伤害：' + str(reports[6]) + '\n'
    res += '场均建筑伤害：' + str(reports[7]) + '\n'
    res += '场均治疗：' + str(reports[8])
    return res


def getLatestComparingStat(playerIdA, playerIdB, total=20):
    reportsA, kdaA, gpmA, xpmA, player_nameA = getLatestGamesStat(playerIdA, total)
    if type(reportsA) == type(""):
        return reportsA
    reportsB, kdaB, gpmB, xpmB, player_nameB = getLatestGamesStat(playerIdB, total)
    if type(reportsB) == type(""):
        return reportsB
    cmp_results = list(map(lambda a, b: '<' if a < b else '=' if a == b else '>', reportsA, reportsB))
    kda_results = '<' if kdaA < kdaB else '=' if kdaA == kdaB else '>'
    gpm_results = '<' if gpmA < gpmB else '=' if gpmA == gpmB else '>'
    xpm_results = '<' if xpmA < xpmB else '=' if xpmA == xpmB else '>'

    res = player_nameA + ' vs ' + player_nameB + '最近' + str(total) + '游戏数据如下：\n'
    res += '胜率：' + str(reportsA[0]) + " " + cmp_results[0] + " " + str(reportsB[0]) + '\n'
    res += 'KDA：' + str(kdaA) + " " + kda_results + " " + str(kdaB) + '\n'
    res += '场均击杀：' + str(reportsA[1]) + " " + cmp_results[1] + " " + str(reportsB[1]) + '\n'
    res += '场均死亡：' + str(reportsA[2]) + " " + cmp_results[2] + " " + str(reportsB[2]) + '\n'
    res += '场均助攻：' + str(reportsA[3]) + " " + cmp_results[3] + " " + str(reportsB[3]) + '\n'
    res += '场均GPM：' + str(gpmA) + " " + gpm_results + " " + str(gpmB) + '\n'
    res += '场均XPM：' + str(xpmA) + " " + xpm_results + " " + str(xpmB) + '\n'
    res += '场均正补：' + str(reportsA[4]) + " " + cmp_results[4] + " " + str(reportsB[4]) + '\n'
    res += '场均反补：' + str(reportsA[5]) + " " + cmp_results[5] + " " + str(reportsB[5]) + '\n'
    res += '场均英雄伤害：' + str(reportsA[6]) + " " + cmp_results[6] + " " + str(reportsB[6]) + '\n'
    res += '场均建筑伤害：' + str(reportsA[7]) + " " + cmp_results[7] + " " + str(reportsB[7]) + '\n'
    res += '场均治疗：' + str(reportsA[8]) + " " + cmp_results[8] + " " + str(reportsB[8])
    return res
