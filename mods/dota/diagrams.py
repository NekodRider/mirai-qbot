# type: ignore
import asyncio
import random
from functools import reduce
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from playwright.async_api import async_playwright

from .constants import api_dict
from .helper import getDotaGamesInfo, getDotaPlayerInfo, getNameDict
from .process import getLatestGamesStat

plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei']
plt.switch_backend('agg')


def getStarScore(reports, gpm):
    participate = (reports[1] + reports[3]) - 10
    if participate > 15:
        participate = 15
    elif participate < 0:
        participate = 0
    participate = round(participate / 15 * 10, 2)

    winrate = round(reports[0] * 8.5 + 1.5, 2)

    hit = reports[4] + reports[5]
    if hit < 100:
        hit = 100
    elif hit > 200:
        hit = 200
    hit = (hit - 100) / 100
    if gpm < 200:
        gpm = 200
    elif gpm > 600:
        gpm = 600
    gpm = (gpm - 200) / 400
    efficiency = round(hit * 2 + gpm * 8, 2)

    damage = reports[6]
    if damage > 25000:
        damage = 25000
    elif damage < 6000:
        damage = 6000
    damage = round((damage - 6000) / 1900, 2)

    push = reports[7] + reports[8]
    if push > 6000:
        push = 6000
    push = round(push / 600, 2)

    raw_data = {
        "参战能力": participate,
        "输出能力": damage,
        "推进能力": push,
        "胜率": winrate,
        "打钱能力": efficiency
    }
    res = {}
    for k, v in raw_data.items():
        if v < 5:
            res[k] = round(np.tanh(v / 5 * 3) * 5, 2)
        else:
            res[k] = v

    return res


def getCompStarStat(playerIdA, playerIdB, total=20):
    ret_a = getLatestGamesStat(playerIdA, total)
    ret_b = getLatestGamesStat(playerIdB, total)
    if not ret_a or not ret_b:
        return f"{playerIdB if ret_a else playerIdA} 不存在!", 0, 0
    reports_a, _, gpm_a, _, player_name_a = ret_a
    reports_b, _, gpm_b, _, player_name_b = ret_b

    raw_data_a = getStarScore(reports_a, gpm_a)
    raw_data_b = getStarScore(reports_b, gpm_b)

    fig = plt.figure(figsize=(4, 4.5))
    ax1 = fig.add_subplot(1, 1, 1, polar=True)
    ax1.set_title(f'{player_name_a} VS {player_name_b} 最近 {str(total)} 场游戏数据对比')
    ax1.set_rlim(0, 10.5)

    value_a = np.array([i for i in raw_data_a.values()]).astype(float)
    value_b = np.array([i for i in raw_data_b.values()]).astype(float)
    label = np.array([j for j in raw_data_a.keys()])

    angle = np.linspace(0, 2 * np.pi, len(value_a), endpoint=False)
    angles = np.concatenate((angle, [angle[0]]))
    value_a = np.concatenate((value_a, [value_a[0]]))
    value_b = np.concatenate((value_b, [value_b[0]]))

    ax1.set_thetagrids(angle * 180 / np.pi, label)
    ax1.plot(angles, value_a, "o-", color='darkorange', label=player_name_a)
    ax1.plot(angles, value_b, "o-", color='royalblue', label=player_name_b)
    ax1.tick_params('y', labelleft=False)
    ax1.set_theta_zero_location('N')

    ax1.fill(angles, value_a, facecolor='darkorange', alpha=0.2)
    ax1.fill(angles, value_b, facecolor='royalblue', alpha=0.2)

    plt.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))

    plt.draw()
    pic_name = str(
        Path(__file__).parent.joinpath(playerIdA + playerIdB + "_star.png"))
    plt.savefig(pic_name)

    return pic_name, player_name_a, player_name_b


def getStarStat(playerId, total=20):
    game_stats = getLatestGamesStat(playerId, total)
    if not game_stats:
        return f"{playerId} 不存在!", 0
    reports, _, gpm, _, player_name = game_stats
    raw_data = getStarScore(reports, gpm)

    fig = plt.figure(figsize=(4, 4.5))
    ax1 = fig.add_subplot(1, 1, 1, polar=True)
    ax1.set_title(player_name + '最近 ' + str(total) + ' 场游戏数据统计')
    ax1.set_rlim(0, 10.5)

    value = np.array([i for i in raw_data.values()]).astype(float)
    label = np.array([j for j in raw_data.keys()])

    angle = np.linspace(0, 2 * np.pi, len(value), endpoint=False)
    angles = np.concatenate((angle, [angle[0]]))
    value = np.concatenate((value, [value[0]]))

    ax1.set_thetagrids(angle * 180 / np.pi, label)
    ax1.plot(angles, value, "o-", color='darkorange')
    ax1.tick_params('y', labelleft=False)
    ax1.set_theta_zero_location('N')

    ax1.fill(angles, value, facecolor='darkorange', alpha=0.2)

    for a, b in zip(angles, value):
        plt.text(a, b, b, ha='center', va='center', fontsize=8)

    plt.draw()
    pic_name = str(Path(__file__).parent.joinpath(playerId + "_star.png"))
    plt.savefig(pic_name)

    return pic_name, player_name


def getWinRateList(playerId, total=20):
    res = []
    player_data = getDotaPlayerInfo(playerId, "/summary")
    games_data = getDotaGamesInfo(playerId, f"?take={total}&include=Player")
    if not player_data:
        return f"{playerId} 不存在!", 0
    if not games_data:
        return f"{playerId} 场次无记录!", 0

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
    winning_rate.append(
        round(pre_win / pre_total * 100, 4) if (pre_total != 0) else 100)
    res.reverse()
    for _, result in enumerate(res):
        pre_total += 1
        if result == 1:
            pre_win += 1
        winning_rate.append(
            round(pre_win / pre_total * 100, 4) if (pre_total != 0) else 100)
    return winning_rate, player_name


def getWinRateGraph(playerId, total=20):
    winning_rate, player_name = getWinRateList(playerId, total)
    if isinstance(winning_rate, str):
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
    pic_name = str(
        Path(__file__).parent.joinpath(playerId + "_winning_rate.png"))
    plt.savefig(pic_name)
    return pic_name, player_name


def getCompWinRateGraph(playerIdList, total=20):
    winning_rate_list = []
    player_name_list = []
    for pid in playerIdList:
        wr, pn = getWinRateList(pid, total)
        if isinstance(wr, str):
            return wr, 0
        winning_rate_list.append(wr)
        player_name_list.append(pn)

    graph_index = range(0, total + 1)

    plt.figure(figsize=(7.5, 5.5))
    plt.title('最近 ' + str(total) + " 场游戏胜率对比")
    pltr = plt.twinx()
    plt.plot(graph_index, wr[0], c="r", label=player_name_list[0])
    plt.scatter(graph_index, wr[0], color="r", s=15)
    pltr.plot(graph_index, wr[1], c="b", label=player_name_list[1])
    pltr.scatter(graph_index, wr[1], color="b", s=15)
    plt.xlabel('场次')
    plt.ylabel('胜率百分比')
    x_major_locator = plt.MultipleLocator(total // 10 if total >= 10 else 1)
    ax = plt.gca()
    ax.xaxis.set_major_locator(x_major_locator)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.xlim(-0.5, total + 0.5)
    plt.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))
    plt.draw()
    pic_name = str(
        Path(__file__).parent.joinpath("".join(playerIdList[:2]) +
                                       "_winning_rate.png"))
    plt.savefig(pic_name)
    return pic_name, player_name_list


async def getDotaStory(matchId):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_viewport_size({"width": 800, "height": 900})
        await page.goto(api_dict["match_story"].format(matchId))
        await page.evaluate("localStorage.setItem('localization', 'zh-CN');")
        await page.reload(wait_until='networkidle')
        name_dict = getNameDict(matchId)
        for hero, name in name_dict.items():
            await page.evaluate(
                f'(()=>{{var html = document.querySelector("body").innerHTML; html = html.split("{hero}").join("{name}"); document.querySelector("body").innerHTML = html}})()',
                force_expr=True)

        not_found = await page.query_selector(".FourOhFour")
        unparsed = await page.query_selector(".unparsed")
        if not_found:
            await browser.close()
            return 404
        if unparsed:
            await page.goto(api_dict["match_request"].format(matchId))
            await asyncio.sleep(5)
            await browser.close()
            return 1

        body = await page.query_selector("body")
        body_bb = await body.bounding_box()
        height = body_bb['height']
        path = str(Path(__file__).parent.joinpath(f'story_{matchId}.png'))
        to_remove = [
            await page.query_selector("#root > div > div"),
            await page.query_selector(".MuiTabs-root"),
            await page.query_selector(".matchButtons"),
        ]
        content = await page.query_selector("#root > div > div:nth-child(3)")
        for i in to_remove:
            await i.evaluate("node => node.style.display='none'")
        await content.screenshot(path=path)
        await browser.close()
        return path
