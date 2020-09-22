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


def getDotaGamesInfo(playerId, matchesArgs=""):
    url = f"https://api.stratz.com/api/v1/Player/{playerId}/matches{matchesArgs}"
    html = request.urlopen(url)
    games_data = json.loads(html.read().decode('utf-8'))
    return games_data


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
    url = f"https://api.stratz.com/api/v1/Player/{playerId}/heroPerformance/{hero_id}"
    html = request.urlopen(url)
    if html.read().decode('utf-8')=="":
        return tuple(0, f"你也配玩{res['hero']}？")
    data = json.loads(html.read().decode('utf-8'))
    res["name"] = getDotaPlayerInfo(playerId)["steamAccount"]["name"]

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