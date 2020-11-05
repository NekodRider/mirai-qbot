from re import sub
import time
import random
import functools
from pathlib import Path
from typing import Callable, Tuple
from .._utils.storage import readJSON, updateJSON

USER_DATA_PATH = Path(__file__).parent.joinpath("users.json")


def args_parser(num, index=None):

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, bot, subject):
            if len(args) < num:
                r = getUserInfo(subject.id)
                userId = r and r["nickname"]
                if userId is not None:
                    if index is not None:
                        a = list(args)
                        a.insert(index, userId)
                        args = tuple(a)
                    else:
                        args += (userId,)
            return func(*args, bot=bot, subject=subject)

        return wrapper

    return decorator


def getUserInfo(qq: int):
    try:
        return list(
            filter(lambda a: a["qq"] == qq, readJSON(USER_DATA_PATH, True,
                                                     [])))[0]
    except IndexError:
        return None


def updateUserInfo(qq: int, info: dict):
    data = readJSON(USER_DATA_PATH, True, [])
    if isinstance(data, dict):
        raise TypeError("Expected list but found:", data)
    targets = list(filter(lambda a: a["qq"] == qq, data))
    if len(targets) == 0:
        info["qq"] = qq
        return updateJSON(USER_DATA_PATH, data + [info])
    index = data.index(targets[0])
    data[index].update(info)
    return updateJSON(USER_DATA_PATH, data)


def humanisticCare(gen: Callable[[int], int], times: int, range: Tuple[int,
                                                                       int]):
    res = gen(times)
    if times == 0:
        return res
    if res > range[1] or res < range[0]:
        return res
    return max((res, humanisticCare(gen, times - 1, range)))


def calcJrrp(groupId: int, qq: int, offset: int = 0) -> int:
    """
    0-100
    因为同 offset 同日期要产生同样的值，且不能在日期加大的时候重复，所以就这么瞎拼一下了
    """
    seed = groupId + qq + int(
        str(offset) + time.strftime("%Y%m%d", time.localtime()))
    random.seed(seed)
    return random.randint(0, 100)
