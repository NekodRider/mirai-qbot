from mirai import Mirai, GroupMessage, Group, MessageChain, Member, Plain, exceptions
from mirai.logger import Session as SessionLogger
from .._utils import parseMsg
from .jrrp import calcJrrp
from ..users import getUserInfo


async def jrrp_handler(*args, sender: Member, event_type):
    '''查询今日人品

    用法: /jrrp'''
    if event_type != "GroupMessage":
        return [Plain(text="尚未支持该类型")]
    target = getUserInfo(sender.id)

    nickname = sender.memberName
    hint = ''
    if target is None:
        hint = '\n\n可以通过 /setname 为自己设定名字哦！'
    else:
        nickname = target['nickname']

    nickname = nickname.upper()
    msg = '%s今日人品为%d，%s'
    rp = calcJrrp(sender.group.id, sender.id)
    postfix = 'NB！！！'
    if rp == 0:
        postfix = 'SB!!!!'
    elif rp < 40:
        postfix = '不NB，但%sNB！' % ('YD' if nickname != 'YD' else 'TD')
    elif rp < 71:
        postfix = 'NB！'
    elif rp < 100:
        postfix = 'NB！！'
    return [Plain(text=(msg+postfix) % (nickname, rp, nickname) + hint)]

COMMANDS = {"jrrp": jrrp_handler}
