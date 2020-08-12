from mirai import Group, Member
from mods.users.user_info_loader import getUserInfo
import time
import random


def jrrpHandler(group: Group, member: Member, *args) -> str:
    """
    return 'YD 今日人品为 99,YDNB！

    0 -> YDSB!!!
    1-20 -> YDSB!!
    21-50 -> YDSB!
    51-80 -> YDNB!
    80-99 -> YDNB!!
    100 -> YDNB!!!
    """
    rp = calcJrrp(group.id, member.id)
    msg = '%s今日人品为%d，%s'
    postfix = 'NB！！！'
    if rp == 0:
        postfix = 'SB!!!!'
    elif rp < 50:
        postfix = '不NB'
    elif rp < 81:
        postfix = 'NB！'
    elif rp < 100:
        postfix = 'NB！！'
    nickname = member.memberName.upper()
    hint = ''
    try:
        nickname = getUserInfo(member.id)['nickname'].upper()
    except:
        hint = '\n\n可以通过 /setName 为自己设定名字哦！'
    return (msg+postfix) % (nickname, rp, nickname) + hint


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
