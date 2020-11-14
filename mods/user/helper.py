from bot.bot import Bot
import time
import random
import functools
from typing import Callable, Tuple, Union


def args_parser(num: int, index: Union[int, None] = None):

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, bot: Bot, subject):
            if len(args) < num:
                nickname = bot.db.get(subject, "nickname")
                if nickname:
                    if index:
                        a = list(args)
                        a.insert(index, nickname)
                        args = tuple(a)
                    else:
                        args += (nickname,)
            return func(*args, bot=bot, subject=subject)

        return wrapper

    return decorator


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
