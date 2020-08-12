from pathlib import Path
from utils.dict_loader import readDict, updateDict

"""
json scheme:

type UserInfo = {
    qq: string,
    nickname: string,
}

type Data = Array<UserInfo>

"""

USER_DATA_PATH = Path(__file__).parent.joinpath('users.json')


def loadUserInfo():
    return readDict(USER_DATA_PATH, True, [])


def getUserInfo(qq: str):
    try:
        return list(filter(lambda a: a['qq'] == qq, loadUserInfo()))[0]
    except IndexError:
        return None


def updateUserInfo(qq: str, info):
    data = loadUserInfo()
    targets = list(filter(lambda a: a['qq'] == qq, data))
    length = len(targets)
    if ('qq' in info and info['qq'] != qq):
        raise Exception('qq number should be same as info')
    if length > 1:
        raise Exception('qq number should be unique')
    if length == 0:
        info['qq'] = qq
        return updateDict(USER_DATA_PATH, data + [info])
    target = targets[0]
    for k, v in info.items():
        target[k] = v
    return updateDict(USER_DATA_PATH, list(filter(lambda a: a['qq'] != qq, data)) + [target])


# updateUserInfo('uck', {'nickname': 'fuckyou', 'oo': 'fuck'})
