import time
from .helper import getDotaGamesInfo, getDotaPlayerInfo, hero_dict, error_codes, getDotaGamesInfoOpenDota

def processInfoOpenDota(playerId):
    games_data = getDotaGamesInfoOpenDota(playerId)
    res = []
    for match in games_data:
        if (time.time() - match["start_time"]) // 3600 > 24:
            break
        t = {}
        t['match_id'] = match['match_id']
        t['time'] = time.strftime("%H:%M", time.localtime(match["start_time"]))
        if match["player_slot"] < 128:
            t['isWin'] = "胜" if match["radiant_win"] else "负"
        else:
            t['isWin'] = "负" if match["radiant_win"] else "胜"
        t['duration'] = "%d:%02d" % (
            match["duration"] // 60, match["duration"] % 60)
        lane_roles = {1: "优势路", 2: "中路　", 3: "劣势路", 4: "打野"}
        if not match["lane_role"]:
            t['role'] = "未知　"
        else:
            t['role'] = lane_roles[match["lane_role"]]
        t['hero'] = hero_dict[str(match["hero_id"])]
        t['kda'] = "%d/%d/%d" % (
            match["kills"], match["deaths"], match["assists"])
        t['hit'] = match["last_hits"]
        t['gpm'] = match["gold_per_min"]
        t['damage'] = match["hero_damage"]
        res.append(t)
    return res

def processInfo(playerId, matchesArgs=""):
    games_data = getDotaGamesInfo(playerId, matchesArgs)
    res = []
    for match in games_data:
        if (time.time() - match["startDateTime"]) // 3600 > 24:
            break
        t = {}
        t['time'] = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(match["startDateTime"]))
        t['isWin'] = "胜" if match["players"][0]["isVictory"] else "负"
        t['duration'] = "%d:%02d" % (
            match["durationSeconds"] // 60, match["durationSeconds"] % 60)
        # imp removed and avgImp so high, using imp2 (imp sub avgImp)
        # if 'imp' in match["players"][0].keys() and 'avgImp' in match.keys():
        #     # official avgImp bug, use 110 as avgImp
        #     #t['imp'] = round(match["players"][0]["imp"] / (match["avgImp"]-20 if match["avgImp"]>20 else match["avgImp"]), 2)
        #     t['imp'] = round(match["players"][0]["imp"] / 110, 2)
        # else:
        #     t['imp'] = 0
        if 'imp2' in match["players"][0].keys():
            t['imp'] = ("+" if match["players"][0]["imp2"] >=
                        0 else "") + str(match["players"][0]["imp2"])
        else:
            t['imp'] = 0
        if 'role' in match["players"][0].keys() and 'lane' in match["players"][0].keys():
            t['role'] = ("优势路" if match["players"][0]["lane"] == 1 else (
                "中路" if match["players"][0]["lane"] == 2 else (
                    "游走" if match["players"][0]["lane"] == 0 else "劣势路"))) + (
                "核心" if match["players"][0]["role"] == 0 else "辅助")
        else:
            t['role'] = "未知"
        t['hero'] = hero_dict[str(match["players"][0]["heroId"])]
        if len(t['hero']) % 2 == 0:
            t['hero'] += chr(12288)
        t['KDA'] = "%d/%d/%d" % (
            match["players"][0]["numKills"], match["players"][0]["numDeaths"], match["players"][0]["numAssists"])
        t['HD'] = "%d/%d" % (match["players"][0]["numLastHits"],
                             match["players"][0]["numDenies"])
        t['GPM'] = match["players"][0]["goldPerMinute"]
        t['damage'] = match["players"][0]["heroDamage"]
        res.append(t)

    return res

def getGamesIn24Hrs(playerId):
    player_data = getDotaPlayerInfo(playerId)
    if type(player_data) == type(""):
        return error_codes[player_data]
    player_name = player_data["steamAccount"]["name"]
    res = processInfoOpenDota(playerId)
    report = player_name
    if len(res) == 0:
        return report + ' 今天是一条咸鱼.'
    lost_count = 0
    for i in res:
        if i['isWin'] == '负':
            lost_count += 1
    report += " 24 小时内白给了 {} 把, 躺赢了 {} 把:\n".format(lost_count, len(res) - lost_count)
    hero_str_len = max([len(x['hero']) for x in res])
    unknown_flag = all([x['role']=='未知　' for x in res])
    for _, i in enumerate(res):
        report += "{:<5} {} 时长{:<6} {} {}{} {:<8} 补刀{:<4} GPM{:<4} 输出{:<6} {}\n".\
            format(i['time'],i['match_id'],i['duration'],i['role'] if not unknown_flag else "",i['hero'],(hero_str_len-len(i['hero']))*'　',
            i['kda'], i['hit'], i['gpm'], i['damage'], i['isWin'])
    return report[:-1]

def getStat(playerId,total=20):
    reports, kda, gpm, xpm, player_name = getLatestGamesStat(playerId,total)
    res = player_name + '最近 ' + str(total) + ' 场游戏总数据统计如下：\n'
    res += '胜率：' + str(reports[0]*100) + '%\n'
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

def getLatestGamesStat(playerId, total=20):
    res = {}
    player_data = getDotaPlayerInfo(playerId, "/summary")
    if type(player_data) == type(""):
        return error_codes[player_data]
    games_data = getDotaGamesInfo(playerId, "?take=" + str(total) + "&include=Player")

    player_name = games_data[0]["players"][0]["steamAccount"]["name"]
    exp = 0
    net = 0
    for _, match in enumerate(games_data):
        res['isVic'] = (1 if match["players"][0]["isVictory"] else 0) + res.get('isVic', 0)
        res['k'] = int(match["players"][0]["numKills"]) + res.get('k', 0)
        res['d'] = int(match["players"][0]["numDeaths"]) + res.get('d', 0)
        res['a'] = int(match["players"][0]["numAssists"]) + res.get('a', 0)
        res['last'] = int(match["players"][0]["numLastHits"]) + res.get('last', 0)
        res['deny'] = int(match["players"][0]["numDenies"]) + res.get('deny', 0)
        res['dmg'] = int(match["players"][0]["heroDamage"]) + res.get('dmg', 0)
        res['tow'] = int(match["players"][0]["towerDamage"]) + res.get('tow', 0)
        res['heal'] = int(match["players"][0]["heroHealing"]) + res.get('heal', 0)
        exp += int(match["players"][0]["experiencePerMinute"])
        net += int(match["players"][0]["goldPerMinute"])

    reports = list(map(lambda value: round(value / total, 2), res.values()))
    kda = round((res['k'] + res['a']) / (res['d'] if res['d'] != 0 else 1), 2)
    gpm = round(net / total, 2)
    xpm = round(exp / total, 2)
    
    return reports, kda, gpm, xpm, player_name


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

    res = player_nameA + ' vs ' + player_nameB + '最近 ' + str(total) + ' 场游戏数据如下：\n'
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


