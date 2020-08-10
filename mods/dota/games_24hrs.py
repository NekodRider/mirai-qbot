import time
import types
from .helper import getDotaGamesInfo, getDotaPlayerInfo, hero_dict, error_codes


def getGamesIn24Hrs(playerId):
    res = []
    player_data = getDotaPlayerInfo(playerId)
    if type(player_data) == type(""):
        return error_codes[player_data]
    player_name = player_data["steamAccount"]["name"]
    games_data = getDotaGamesInfo(playerId)

    for match in games_data:
        if (time.time() - match["startDateTime"]) // 3600 > 24:
            break
        t = {}
        # server in utc+3
        t['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(match["startDateTime"] + 5 * 60 * 60))
        t['isWin'] = "胜" if match["players"][0]["isVictory"] else "负"
        t['duration'] = "%d:%02d" % (match["durationSeconds"] // 60, match["durationSeconds"] % 60)
        if 'imp' in match["players"][0].keys() and 'avgImp' in match.keys():
            t['imp'] = round(match["players"][0]["imp"] / match["avgImp"], 2)
        else:
            t['imp'] = 0
        if 'role' in match["players"][0].keys() and 'lane' in match["players"][0].keys():
            t['role'] = ("优势路" if match["players"][0]["lane"] == 1 else (
                "中路" if match["players"][0]["lane"] == 2 else "劣势路")) + (
                            "核心" if match["players"][0]["role"] == 0 else "辅助")
        else:
            t['role'] = "未知"
        t['hero'] = hero_dict[str(match["players"][0]["heroId"])]
        if len(t['hero']) % 2 == 0:
            t['hero'] += chr(12288)
        t['KDA'] = "%d/%d/%d" % (
            match["players"][0]["numKills"], match["players"][0]["numDeaths"], match["players"][0]["numAssists"])
        t['HD'] = "%d/%d" % (match["players"][0]["numLastHits"], match["players"][0]["numDenies"])
        t['GPM'] = match["players"][0]["goldPerMinute"]
        t['damage'] = match["players"][0]["heroDamage"]
        res.append(t)
    report = player_name
    if len(res) == 0:
        return report + ' 今天是一条咸鱼.'
    lost_count = 0
    for i in res:
        if i['isWin'] == '负':
            lost_count += 1
    report += " 24 小时内白给了 {} 把, 躺赢了 {} 把:\n".format(lost_count, len(res) - lost_count)
    for _, i in enumerate(res):
        report += "{:<19} 时长{:<6} {:<6} {:<6} {:<8}  补刀{:<6}{}  GPM{:<4}  输出{:<6}{} 表现评分{:<4}{}  {}\n".\
            format(i['time'],i['duration'],i['role'],i['hero'],
            i['KDA'], i['HD'],chr(12288),i['GPM'],i['damage'],
            chr(12288),i["imp"],chr(12288),i['isWin'])
    return report[:-1]

