from pathlib import Path
from .._utils import readJSON, updateJSON

"""
json scheme:

type UserInfo = {
    qq: string,
    nickname: string,
}

type Data = Array<UserInfo>

"""

USER_DATA_PATH = Path(__file__).parent.joinpath('users.json')

def getUserInfo(qq: str):
    try:
        return list(filter(lambda a: a['qq'] == qq, readJSON(USER_DATA_PATH, True, [])))[0]
    except IndexError:
        return None


def updateUserInfo(qq: str, info):
    data = readJSON(USER_DATA_PATH, True, [])
    targets = list(filter(lambda a: a['qq'] == qq, data))
    length = len(targets)
    if ('qq' in info and info['qq'] != qq):
        raise Exception('qq number should be same as info')
    if length > 1:
        raise Exception('qq number should be unique')
    if length == 0:
        info['qq'] = qq
        return updateJSON(USER_DATA_PATH, data + [info])
    target = targets[0]
    for k, v in info.items():
        target[k] = v
    return updateJSON(USER_DATA_PATH, list(filter(lambda a: a['qq'] != qq, data)) + [target])


# updateUserInfo('uck', {'nickname': 'fuckyou', 'oo': 'fuck'})
