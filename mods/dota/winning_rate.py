from .helper import getDotaPlayerInfo, getDotaGamesInfo, error_codes
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

from functools import reduce


def norm(data):
    range = np.max(data) - np.min(data)
    return ((data - np.min(data)) / range) * 6 - 3


def denomre(data, max, min):
    range = max - min
    return ((data + 1) / 2 * range) + min


def getWinningRateGraph(playerId, total=50):
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
    graph_index = range(0, latest_total + 1)
    graph_max = np.max(winning_rate)
    graph_min = np.min(winning_rate)
    graph_range = graph_max - graph_min

    plt.figure()
    plt.title('Winning rate in the latest ' + str(total) + " games")
    plt.ylim(graph_min - (graph_range) / 25, graph_max + (graph_range) / 25)
    plt.plot(graph_index, winning_rate, color="red", label="Winning rate")
    plt.scatter(graph_index, winning_rate, color="red", s=15)
    plt.legend()
    plt.draw()
    pic_name = str(Path(__file__).parent.joinpath(playerId + "_winning_rate.png"))
    plt.savefig(pic_name)
    return pic_name, player_name
