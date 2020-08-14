from mirai import Mirai, GroupMessage, Group, MessageChain, Member, Plain, exceptions
from mirai.logger import Session as SessionLogger
from .._utils import parseMsg
from .jrrp import calcJrrp
from ..users import getUserInfo


async def jrrp_handler(*args, sender, event_type):
    """
    return 'YD 今日人品为 99,YDNB！

    0 -> YDSB!!!
    1-20 -> YDSB!!
    21-50 -> YDSB!
    51-80 -> YDNB!
    80-99 -> YDNB!!
    100 -> YDNB!!!
    """
    if event_type != "GroupMessage":
        return [Plain(text="尚未支持该类型")]
    rp = calcJrrp(sender.group.id, sender.id)
    msg = '%s今日人品为%d，%s'
    postfix = 'NB！！！'
    if rp == 0:
        postfix = 'SB!!!!'
    elif rp < 50:
        postfix = '不NB，但YDNB！'
    elif rp < 81:
        postfix = 'NB！'
    elif rp < 100:
        postfix = 'NB！！'
    nickname = sender.memberName.upper()
    hint = ''
    try:
        nickname = getUserInfo(sender.id)['nickname'].upper()
    except:
        hint = '\n\n可以通过 /setname 为自己设定名字哦！'
    return [Plain(text=(msg+postfix) % (nickname, rp, nickname) + hint)]

COMMANDS = {"jrrp": jrrp_handler}
