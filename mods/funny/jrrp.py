from mirai import Group, Member
from mods.users.user_info_loader import getUserInfo
import time
import random


def calcJrrp(groupId: int, qq: int) -> int:
    """
    0-100
    """
    seed = groupId + qq + int(time.strftime("%Y%m%d", time.localtime()))
    random.seed(seed)
    return random.randint(0, 100)

# class FUCK:
#     def __init__(self):
#         self.id = 0
#         self.memberName = 'fuck'


# a = FUCK()

# jrrpHandler(a, a)
