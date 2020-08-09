from urllib import request
from pathlib import Path
from datetime import datetime
import time
import json


hero_dict = {'1': '敌法师', '2': '斧王', '3': '祸乱之源', '4': '血魔', '5': '水晶室女', '6': '卓尔游侠', '7': '撼地者', '8': '主宰', '9': '米拉娜', '10': '变体精灵', '11': '影魔', '12': '幻影长矛手', '13': '帕克', '14': '帕吉', '15': '剃刀', '16': '沙王', '17': '风暴之灵', '18': '斯温', '19': '小小', '20': ' 复仇之魂', '21': '风行者', '22': '宙斯', '23': '昆卡', '25': '莉娜', '26': '莱恩', '27': '暗影萨满', '28': '斯拉达', '29': '潮汐猎人', '30': '巫医', '31': '巫妖', '32': '力丸', '33': '谜团', '34': '修补匠', '35': '狙击手', '36': '瘟疫法师', '37': '术士', '38': '兽王', '39': '痛苦女王', '40': '剧毒术士', '41': '虚空假面', '42': '冥魂大帝', '43': '死亡先知', '44': '幻影刺客', '45': '帕格纳', '46': '圣堂刺客', '47': '冥界亚龙', '48': '露娜', '49': '龙骑士', '50': '戴泽', '51': '发条技师', '52': '拉席克', '53': '先知', '54': '噬魂鬼', '55': '黑暗贤者', '56': '克林克兹', '57': '全能骑士', '58': '魅惑魔女', '59': '哈斯卡', '60': '暗夜魔王', '61': '育母蜘蛛', '62': '赏金猎人', '63': '编织者', '64': '杰奇洛', '65': '蝙蝠骑士', '66': '陈', '67': '幽鬼', '68': '远古冰魄', '69': '末日使者', '70': '熊战士', '71': '裂魂人', '72': '矮人直升机', '73': '炼金术士', '74': '祈求者', '75': '沉默术士', '76': '殁境神蚀者', '77': '狼人', '78': '酒仙', '79': '暗影恶魔', '80': '德鲁伊', '81': '混沌骑士', '82': '米波', '83': '树精卫士', '84': '食人魔魔法师', '85': '不朽尸王', '86': '拉比克', '87': '干扰者', '88': '司夜刺客', '89': '娜迦海妖', '90': '光之守卫', '91': '艾欧', '92': '维萨吉', '93': '斯拉克', '94': '美杜莎', '95': '巨魔战将', '96': '半人马战行者', '97': '马格纳斯', '98': '伐木机', '99': '钢背兽', '100': '巨牙海民', '101': '天怒法师', '102': '亚巴顿', '103': '上古巨神', '104': '军团指挥官', '105': '工程师', '106': '灰烬之灵', '107': '大地之灵', '108': '孽主', '109': '恐怖利刃', '110': '凤凰', '111': '神谕者', '112': '寒冬飞龙', '113': '天穹守望者', '114': '齐天大圣', '119': '邪影芳灵', '120': '石鳞剑士', '121': '天涯墨客', '126': 'Void Spirit', '128': 'Snapfire', '129': '玛尔斯'}

def readDict():
    with open(Path(__file__).parent.joinpath("dota_id.json"),encoding='utf-8') as f:
        d = json.loads(f.read())
    return d

def updateDict(d):
    with open(Path(__file__).parent.joinpath("dota_id.json"),'w',encoding='utf-8') as f:
        f.write(json.dumps(d))

def getDotaInfo(playerId):
    url = "https://api.stratz.com/api/v1/Player/"+ playerId
    try:
        html = request.urlopen(url)
    except:
        return "未找到玩家"
    data = json.loads(html.read().decode('utf-8'))
    player_name = data["steamAccount"]["name"]
    url = "https://api.stratz.com/api/v1/Player/"+ playerId+"/matches"
    html = request.urlopen(url)
    data = json.loads(html.read().decode('utf-8'))
    res = []
    for match in data:
        if (time.time() - match["startDateTime"])//3600> 24:
            break
        t = {}
        # server in utc+3
        t['time'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(match["startDateTime"]+5*60*60))
        t['isWin'] = "胜" if match["players"][0]["isVictory"] else "负"
        t['duration'] = "%d:%02d" % (match["durationSeconds"]//60,match["durationSeconds"]%60)
        if 'imp' in match["players"][0].keys() and 'avgImp' in match.keys():
            t['imp'] = round(match["players"][0]["imp"]/match["avgImp"],2)
        else:
            t['imp'] = 0
        if 'role' in match["players"][0].keys() and 'lane' in match["players"][0].keys():
            t['role'] = ("优势路" if match["players"][0]["lane"]==1 else ("中路" if match["players"][0]["lane"]==2 else "劣势路")) + ("核心" if match["players"][0]["role"]==0 else "辅助") 
        else:
            t['role'] = "未知"
        t['hero'] = hero_dict[str(match["players"][0]["heroId"])]
        if len(t['hero'])%2==0:
            t['hero'] += chr(12288)
        t['KDA'] = "%d/%d/%d" % (match["players"][0]["numKills"],match["players"][0]["numDeaths"],match["players"][0]["numAssists"])
        t['HD'] = "%d/%d" % (match["players"][0]["numLastHits"],match["players"][0]["numDenies"])
        t['GPM'] = match["players"][0]["goldPerMinute"]
        t['damage'] = match["players"][0]["heroDamage"]
        res.append(t)
    
    report = player_name
    if len(res)==0:
        return report+' 今天是一条咸鱼.'
    lost_count=0
    for i in res:
        if i['isWin']=='负':
            lost_count+=1
    report +=" 24 小时内白给了 {} 把, 躺赢了 {} 把:\n".format(lost_count,len(res)-lost_count)
    for _,i in enumerate(res):
        report+="{:<19} 时长{:<6} {:<6} {:<6} {:<8}  补刀{:<6}{}  GPM{:<4}  输出{:<6}{} 表现评分{:<4}{}  {}\n".format(i['time'],i['duration'],i['role'],i['hero'],i['KDA'],i['HD'],chr(12288),i['GPM'],i['damage'],chr(12288),i["imp"],chr(12288),i['isWin'])
    return report[:-1]
