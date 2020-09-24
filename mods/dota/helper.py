from urllib import request
from pathlib import Path
import json
import types
import time


hero_dict = {'1': '敌法师', '2': '斧王', '3': '祸乱之源', '4': '血魔', '5': '水晶室女', '6': '卓尔游侠', '7': '撼地者', '8': '主宰', '9': '米拉娜', '10': '变体精灵', '11': '影魔', '12': '幻影长矛手', '13': '帕克', '14': '帕吉', '15': '剃刀', '16': '沙王', '17': '风暴之灵', '18': '斯温', '19': '小小', '20': ' 复仇之魂', '21': '风行者', '22': '宙斯', '23': '昆卡', '25': '莉娜', '26': '莱恩', '27': '暗影萨满', '28': '斯拉达', '29': '潮汐猎人', '30': '巫医', '31': '巫妖', '32': '力丸', '33': '谜团', '34': '修补匠', '35': '狙击手', '36': '瘟疫法师', '37': '术士', '38': '兽王', '39': '痛苦女王', '40': '剧毒术士', '41': '虚空假面', '42': '冥魂大帝', '43': '死亡先知', '44': '幻影刺客', '45': '帕格纳', '46': '圣堂刺客', '47': '冥界亚龙', '48': '露娜', '49': '龙骑士', '50': '戴泽', '51': '发条技师', '52': '拉席克', '53': '先知', '54': '噬魂鬼', '55': '黑暗贤者', '56': '克林克兹', '57': '全能骑士', '58': '魅惑魔女', '59': '哈斯卡', '60': '暗夜魔王', '61': '育母蜘蛛', '62': '赏金猎人', '63': '编织者',
             '64': '杰奇洛', '65': '蝙蝠骑士', '66': '陈', '67': '幽鬼', '68': '远古冰魄', '69': '末日使者', '70': '熊战士', '71': '裂魂人', '72': '矮人直升机', '73': '炼金术士', '74': '祈求者', '75': '沉默术士', '76': '殁境神蚀者', '77': '狼人', '78': '酒仙', '79': '暗影恶魔', '80': '德鲁伊', '81': '混沌骑士', '82': '米波', '83': '树精卫士', '84': '食人魔魔法师', '85': '不朽尸王', '86': '拉比克', '87': '干扰者', '88': '司夜刺客', '89': '娜迦海妖', '90': '光之守卫', '91': '艾欧', '92': '维萨吉', '93': '斯拉克', '94': '美杜莎', '95': '巨魔战将', '96': '半人马战行者', '97': '马格纳斯', '98': '伐木机', '99': '钢背兽', '100': '巨牙海民', '101': '天怒法师', '102': '亚巴顿', '103': '上古巨神', '104': '军团指挥官', '105': '工程师', '106': '灰烬之灵', '107': '大地之灵', '108': '孽主', '109': '恐怖利刃', '110': '凤凰', '111': '神谕者', '112': '寒冬飞龙', '113': '天穹守望者', '114': '齐天大圣', '119': '邪影芳灵', '120': '石鳞剑士', '121': '天涯墨客', '126': '虚无之灵', '128': '电炎绝手', '129': '玛尔斯'}
error_codes = {'404_NOT_FOUND': '请输入正确steam ID!',
               'NO_SUCH_PLAYER': '该玩家不存在!'}

dota_dict_path = Path(__file__).parent.joinpath("dota_id.json")


def getDotaPlayerInfo(playerId, playerArgs=""):
    url = f"https://api.stratz.com/api/v1/Player/{playerId}{playerArgs}"
    try:
        html = request.urlopen(url)
    except:
        return '404_NOT_FOUND'
    player_data = json.loads(html.read().decode('utf-8'))
    if playerArgs == '' and player_data["steamAccount"]["name"] == 'Unknown':
        return 'NO_SUCH_PLAYER'
    return player_data

def getDotaGamesInfoOpenDota(playerId):
    url = f"https://api.opendota.com/api/players/{playerId}/recentMatches"
    req = request.Request(url)
    req.add_header("User-Agent","Chrome/69.0.3497.81 Safari/537.36")
    html = request.urlopen(req)
    games_data = json.loads(html.read().decode('utf-8'))
    res = []
    for match in games_data:
        if (time.time() - match["start_time"]) // 3600 > 24:
            break
        t = {}
        t['time'] = time.strftime("%m-%d %H:%M", time.localtime(match["start_time"]))
        if match["player_slot"]<128:
            t['isWin'] = "胜" if match["radiant_win"] else "负"
        else:
            t['isWin'] = "负" if match["radiant_win"] else "胜"
        t['duration'] = "%d:%02d" % (match["duration"] // 60, match["duration"] % 60)
        lane_roles = {1:"优势路",2:"中路　",3:"劣势路",4:"打野"}
        t['role'] = lane_roles[match["lane_role"]]
        t['hero'] = hero_dict[str(match["hero_id"])]
        t['kda'] = "%d/%d/%d" % (
            match["kills"], match["deaths"], match["assists"])
        t['hit'] = match["last_hits"]
        t['gpm'] = match["gold_per_min"]
        t['damage'] = match["hero_damage"]
        res.append(t)
    return res

def getDotaGamesInfo(playerId, matchesArgs=""):
    url = f"https://api.stratz.com/api/v1/Player/{playerId}/matches{matchesArgs}"
    html = request.urlopen(url)
    games_data = json.loads(html.read().decode('utf-8'))
    res = []
    for match in games_data:
        if (time.time() - match["startDateTime"]) // 3600 > 24:
            break
        t = {}
        t['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(match["startDateTime"]))
        t['isWin'] = "胜" if match["players"][0]["isVictory"] else "负"
        t['duration'] = "%d:%02d" % (match["durationSeconds"] // 60, match["durationSeconds"] % 60)
        # imp removed and avgImp so high, using imp2 (imp sub avgImp)
        # if 'imp' in match["players"][0].keys() and 'avgImp' in match.keys():
        #     # official avgImp bug, use 110 as avgImp
        #     #t['imp'] = round(match["players"][0]["imp"] / (match["avgImp"]-20 if match["avgImp"]>20 else match["avgImp"]), 2)
        #     t['imp'] = round(match["players"][0]["imp"] / 110, 2)
        # else:
        #     t['imp'] = 0
        if 'imp2' in match["players"][0].keys():
            t['imp'] = ("+" if match["players"][0]["imp2"]>=0 else "") + str(match["players"][0]["imp2"])
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
        t['HD'] = "%d/%d" % (match["players"][0]["numLastHits"], match["players"][0]["numDenies"])
        t['GPM'] = match["players"][0]["goldPerMinute"]
        t['damage'] = match["players"][0]["heroDamage"]
        res.append(t)

    return res


def steam_html_process(raw_str):
    left = 0
    while 1:
        l = raw_str[left:].find("[")
        if l == -1:
            break
        elif "img" != raw_str[left+l+1:left+l+4]:
            r = raw_str[left:].find("]")
            raw_str = raw_str[:left+l] + raw_str[left+r+1:]
            left = left+l
        else:
            r = raw_str[left:].find("]")
            r = raw_str[left+r+1:].find("]")
            left = left + r + 1
    return raw_str


def getDotaNews(timeout=300):
    url = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=570&feeds=steam_community_announcements,steam_updates&count=1"
    html = request.urlopen(url)
    news_list = json.loads(html.read().decode('utf-8'))["appnews"]["newsitems"]
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
    for k,v in hero_dict.items():
        if v == heroName:
            res['hero'] = v
            hero_id = k
            break
    if hero_id == -1:
        return 0
    res["name"] = getDotaPlayerInfo(playerId)["steamAccount"]["name"]
    url = f"https://api.stratz.com/api/v1/Player/{playerId}/heroPerformance/{hero_id}?gameMode=1,2,3,4"
    html = request.urlopen(url)
    txt = html.read().decode('utf-8')
    if txt=="":
        return (0, f"{res['name']} 也配玩 {res['hero']}？")
    data = json.loads(txt)
    

    res["win_stat"] = f"{round(data['winCount']/data['matchCount']*100,2)}% - {data['winCount']}W/{data['matchCount']-data['winCount']}L"
    res["kda"] = f"{int(data['avgNumKills'])}/{int(data['avgNumDeaths'])}/{int(data['avgNumAssists'])}"
    res["gpm"] = int(data['avgGoldPerMinute'])

    def getLaneMatchCount(elem):
        return elem["laneMatchCount"]
    def getRoleLaneMatchCount(elem):
        return elem["lanes"][0]["laneMatchCount"]

    for role in data["position"]:
        role["lanes"].sort(key=getLaneMatchCount, reverse=True)

    data["position"].sort(key=getRoleLaneMatchCount, reverse=True)
    role = data["position"][0]

    res["role"] = f"在{round(role['lanes'][0]['laneMatchCount']/data['matchCount']*100,2)}%的比赛中担任"
    res["role"] += "优势路" if role["lanes"][0]["laneType"] == 1 else ("中路" if role["lanes"][0]["laneType"] == 2 else ("游走" if role["lanes"][0]["laneType"] == 0 else "劣势路"))
    res["role"] += '核心' if role['roleType']==0 else '辅助'
    result = f"{res['name']} 使用 {res['hero']} {res['role']}\n胜率：{res['win_stat']}  KDA：{res['kda']}  GPM：{res['gpm']}"
    return result