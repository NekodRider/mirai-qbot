import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from functools import reduce
import random
import asyncio
from pyppeteer import launch

from .helper import getDotaPlayerInfo, getDotaGamesInfo, error_codes, getNameDict
from .games import getLatestGamesStat

plt.rcParams['font.sans-serif']=['WenQuanYi Micro Hei']

def getStarScore(reports, gpm):
    participate = (reports[1] + reports[3])-10
    if participate > 15:
        participate = 15
    elif participate < 0:
        participate = 0
    participate = round(participate/15*10,2)

    winrate = round(reports[0]*8.5+1.5,2)
    
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
    if damage > 25000:
        damage = 25000
    elif damage < 6000:
        damage = 6000
    damage = round((damage - 6000) / 1900,2)

    push = reports[7] + reports[8]
    if push>6000:
        push = 6000
    push = round(push/600 ,2)

    raw_data={"参战能力":participate,"输出能力":damage,"推进能力":push,"胜率":winrate,"打钱能力":efficiency}
    res = {}
    for k,v in raw_data.items():
        if v<5:
            res[k] = round(np.tanh(v/5*3)*5,2)
        else:
            res[k] = v

    return res

def getCompStarStat(playerIdA, playerIdB, total=20):
    reports_a, _, gpm_a, _, player_name_a = getLatestGamesStat(playerIdA,total)
    if type(reports_a) == type(""):
        return reports_a, 0, 0
    reports_b, _, gpm_b, _, player_name_b = getLatestGamesStat(playerIdB,total)
    if type(reports_b) == type(""):
        return reports_b, 0, 0

    raw_data_a = getStarScore(reports_a,gpm_a)
    raw_data_b = getStarScore(reports_b,gpm_b)

    fig=plt.figure(figsize=(4, 4.5))
    ax1=fig.add_subplot(1,1,1,polar=True)
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

    fig=plt.figure(figsize=(4, 4.5))
    ax1=fig.add_subplot(1,1,1,polar=True)
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

def getWinRateList(playerId, total=20):
    res = []
    player_data = getDotaPlayerInfo(playerId, "/summary")
    if type(player_data) == type(""):
        return error_codes[player_data], 0
    games_data = getDotaGamesInfo(playerId, "?take=" + str(total) + "&include=Player")

    player_name = games_data[0]["players"][0]["steamAccount"]["name"]
    for _, match in enumerate(games_data):
        res.append(1 if match["players"][0]["isVictory"] else 0)


    latest_total = len(games_data)
    latest_win = reduce(lambda a, b: a + b, res)
    all_total = player_data["allTime"]["matches"]["matchCount"]
    total_win = player_data["allTime"]["matches"]["win"]
    pre_total = all_total - latest_total
    pre_win = total_win - latest_win

    winning_rate = []
    winning_rate.append(round(pre_win / pre_total * 100, 4) if (pre_total != 0) else 100)
    res.reverse()
    for _, result in enumerate(res):
        pre_total += 1
        if result == 1:
            pre_win += 1
        winning_rate.append(round(pre_win / pre_total * 100, 4) if (pre_total != 0) else 100)
    return winning_rate, player_name

def getWinRateGraph(playerId, total=20):
    winning_rate, player_name = getWinRateList(playerId,total)
    if type(winning_rate) == type(""):
        return winning_rate, 0
    graph_index = range(0, total + 1)
    graph_max = np.max(winning_rate)
    graph_min = np.min(winning_rate)
    graph_range = graph_max - graph_min


    plt.figure()
    plt.title('最近 ' + str(total) + " 场游戏胜率变化图")
    plt.ylim(graph_min - (graph_range) / 25, graph_max + (graph_range) / 25)
    plt.plot(graph_index, winning_rate, color="red", label="胜率")
    plt.scatter(graph_index, winning_rate, color="red", s=15)
    plt.legend()
    plt.draw()
    pic_name = str(Path(__file__).parent.joinpath(playerId + "_winning_rate.png"))
    plt.savefig(pic_name)
    return pic_name, player_name

def getCompWinRateGraph(playerIdList, total=20):
    winning_rate_list = []
    player_name_list = []
    graph_max, graph_min = 0, 100
    for pid in playerIdList:
        wr, pn = getWinRateList(pid,total)
        if type(wr) == type(""):
            return wr, 0
        graph_max = np.max(wr + [graph_max])
        graph_min = np.min(wr + [graph_min])
        winning_rate_list.append(wr)
        player_name_list.append(pn)
    
    graph_index = range(0, total + 1)

    plt.figure(figsize=(7.5, 5.5))
    plt.title('最近 ' + str(total) + " 场游戏胜率对比")
    for no,wr in enumerate(winning_rate_list):
        color = [random.random() for i in range(3)]
        plt.plot(graph_index, wr, color=color, label=player_name_list[no])
        plt.scatter(graph_index, wr, color=color, s=15)
    plt.xlabel('场次')
    plt.ylabel('胜率百分比')
    x_major_locator=plt.MultipleLocator(total//10 if total>=10 else 1)
    ax=plt.gca()
    ax.xaxis.set_major_locator(x_major_locator)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.xlim(-0.5,total+0.5)
    plt.ylim(graph_min-0.5,graph_max+1.5)
    plt.legend(loc='upper right',bbox_to_anchor=(1.1, 1.1))
    plt.draw()
    pic_name = str(Path(__file__).parent.joinpath("".join(playerIdList[:2]) + "_winning_rate.png"))
    plt.savefig(pic_name)
    return pic_name, player_name_list

async def getDotaStory(matchId):
    browser = await launch(args=['--no-sandbox'])
    page = await browser.newPage()
    await page.setViewport({"width": 800,"height": 900})
    await page.goto(f'https://www.opendota.com/matches/{matchId}/story')
    await page.evaluate("localStorage.setItem('localization', 'zh-CN');")
    await page.reload({'waitUntil' : 'networkidle0'})
    name_dict = getNameDict(matchId)
    for hero,name in name_dict.items():
        await page.evaluate(f'(()=>{{var html = document.querySelector("body").innerHTML; html = html.split("{hero}").join("{name}"); document.querySelector("body").innerHTML = html}})()',force_expr=True)

    not_found = await page.querySelector(".FourOhFour")
    unparsed = await page.querySelector(".unparsed")
    if not_found:
        await browser.close()
        return 404
    if unparsed:
        await page.goto(f'https://www.opendota.com/request#{matchId}')
        await asyncio.sleep(5)
        await browser.close()
        return 1

    body = await page.querySelector("body")
    body_bb = await body.boundingBox()
    height = body_bb['height']
    path = str(Path(__file__).parent.joinpath(f'story_{matchId}.png'))
    await page.screenshot({'path': path,'clip':{'x':0,'y':180,'width':800,'height':height-320}})
    await browser.close()
    return path
