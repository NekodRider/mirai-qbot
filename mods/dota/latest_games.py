from .helper import getDotaPlayerInfo, getDotaGamesInfo, error_codes
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

plt.rcParams['font.sans-serif']=['WenQuanYi Micro Hei']

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

def getStarScore(reports, gpm):
    participate = (reports[1] + reports[3])-10
    if participate > 15:
        participate = 15
    elif participate < 0:
        participate = 0
    participate = round(participate/15*10,2)

    winrate = round(reports[0]*10,2)
    
    hit = reports[4] + reports[5]
    if hit<100:
        hit = 100
    elif hit > 200:
        hit = 200
    hit = (hit - 100) / 100
    if gpm<200:
        gpm = 200
    elif gpm > 600:
        gpm = 600
    gpm = (gpm - 200) / 400
    efficiency = round(hit*2 + gpm * 8,2)

    damage = reports[6]
    if damage > 23000:
        damage = 23000
    elif damage < 13000:
        damage = 13000
    damage = round((damage - 13000) / 1000,2)

    push = reports[7] + reports[8]
    if push>6000:
        push = 6000
    push = round(push/600 ,2)

    raw_data={"参战能力":participate,"输出能力":damage,"推进能力":push,"胜率":winrate,"打钱能力":efficiency}
    for k in raw_data.keys():
        if raw_data[k]==0:
            raw_data[k] = 0.15

    return raw_data

def getCompStarStat(playerIdA, playerIdB, total=20):
    reports_a, _, gpm_a, _, player_name_a = getLatestGamesStat(playerIdA,total)
    if type(reports_a) == type(""):
        return reports_a, 0, 0
    reports_b, _, gpm_b, _, player_name_b = getLatestGamesStat(playerIdB,total)
    if type(reports_b) == type(""):
        return reports_b, 0, 0

    raw_data_a = getStarScore(reports_a,gpm_a)
    raw_data_b = getStarScore(reports_b,gpm_b)

    fig=plt.figure(figsize=(8,4))
    ax1=fig.add_subplot(1,2,1,polar=True)
    ax1.set_title(f'{player_name_a} VS {player_name_b} 最近 {str(total)} 场游戏数据对比')
    ax1.set_rlim(0,10.5)

    value_a=np.array([i for i in raw_data_a.values()]).astype(float)
    value_b=np.array([i for i in raw_data_b.values()]).astype(float)
    label=np.array([j for j in raw_data_a.keys()])

    angle = np.linspace(0, 2*np.pi, len(value_a), endpoint=False)
    angles = np.concatenate((angle, [angle[0]]))
    value_a = np.concatenate((value_a, [value_a[0]]))
    value_b = np.concatenate((value_b, [value_b[0]]))

    ax1.set_thetagrids(angle*180/np.pi, label)
    ax1.plot(angles,value_a,"o-",color='darkorange',label=player_name_a)
    ax1.plot(angles,value_b,"o-",color='royalblue',label=player_name_b)
    ax1.tick_params('y', labelleft=False)
    ax1.set_theta_zero_location('N')
    
    ax1.fill(angles,value_a,facecolor='darkorange', alpha=0.2)
    ax1.fill(angles,value_b,facecolor='royalblue', alpha=0.2)

    plt.legend(loc='upper right',bbox_to_anchor=(1.1, 1.1))

    plt.draw()
    pic_name = str(Path(__file__).parent.joinpath(playerIdA + playerIdB + "_star.png"))
    plt.savefig(pic_name)
    
    return pic_name, player_name_a, player_name_b

def getStarStat(playerId,total=20):
    reports, _, gpm, _, player_name = getLatestGamesStat(playerId,total)
    if type(reports) == type(""):
        return reports, 0
    raw_data=getStarScore(reports,gpm)

    fig=plt.figure(figsize=(8,4))
    ax1=fig.add_subplot(1,2,1,polar=True)
    ax1.set_title(player_name + '最近 ' + str(total) + ' 场游戏数据统计')
    ax1.set_rlim(0,10.5)

    value=np.array([i for i in raw_data.values()]).astype(float)
    label=np.array([j for j in raw_data.keys()])

    angle = np.linspace(0, 2*np.pi, len(value), endpoint=False)
    angles = np.concatenate((angle, [angle[0]]))
    value = np.concatenate((value, [value[0]]))

    ax1.set_thetagrids(angle*180/np.pi, label)
    ax1.plot(angles,value,"o-",color='darkorange')
    ax1.tick_params('y', labelleft=False)
    ax1.set_theta_zero_location('N')
    
    ax1.fill(angles,value,facecolor='darkorange', alpha=0.2)

    for a, b in zip(angles, value):  
        plt.text(a, b, b,ha='center', va='center', fontsize=8)  

    plt.draw()
    pic_name = str(Path(__file__).parent.joinpath(playerId + "_star.png"))
    plt.savefig(pic_name)
    
    return pic_name, player_name

