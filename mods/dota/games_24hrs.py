import time
import types

from mirai.event.message.components import Unknown
from .helper import getDotaGamesInfo, getDotaPlayerInfo, hero_dict, error_codes, getDotaGamesInfoOpenDota


def getGamesIn24Hrs(playerId):
    player_data = getDotaPlayerInfo(playerId)
    if type(player_data) == type(""):
        return error_codes[player_data]
    player_name = player_data["steamAccount"]["name"]
    res = getDotaGamesInfoOpenDota(playerId)
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

