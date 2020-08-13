from mirai import Group, Member
import time
import random


def calcJrrp(groupId: int, qq: int) -> int:
    """
    0-100
    """
    seed = groupId + qq + int(time.strftime("%Y%m%d", time.localtime()))
    random.seed(seed)
    return random.randint(0, 100)
