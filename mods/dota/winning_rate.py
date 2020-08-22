from .helper import getDotaPlayerInfo, getDotaGamesInfo, error_codes
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from functools import reduce
import random


plt.rcParams['font.sans-serif']=['WenQuanYi Micro Hei']

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