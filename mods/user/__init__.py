from typing import Union

from graia.application.friend import Friend
from graia.application.group import Member
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain

from bot import Bot
from bot import defaultLogger as logger

from .helper import args_parser, calcJrrp, humanisticCare

__all__ = ["args_parser"]


async def setname_handler(*args, bot: Bot, subject: Union[Member, Friend]):
    '''设置昵称

    用法: /setname 昵称'''
    if len(args) == 0:
        return MessageChain.create([Plain('使用示例: /setname yd')])
    [name, *_] = args
    oldName = bot.db.get(subject, "nickname")
    try:
        bot.db.set(subject, {'nickname': name})
        return MessageChain.create(
            [Plain('成功从' + (oldName if oldName else '-未设定-') + '变更为' + name)])
    except Exception as e:
        logger.debug(e)
        return MessageChain.create([Plain("修改失败qwq")])


async def name_handler(*args, bot: Bot, subject: Union[Member, Friend]):
    '''显示昵称

    用法: /name'''
    name = bot.db.get(subject, "nickname")
    return MessageChain.create([
        Plain(('你的名字是 ' + name + ' ！') if name else '还没设定哦，通过 /setname 修改名字~')
    ])


async def jrrp_handler(*args, bot: Bot, subject: Union[Member, Friend]):
    '''查询今日人品

    用法: /jrrp'''
    nickname = bot.db.get(subject, "nickname")
    hint = ''
    if not nickname:
        hint = '\n\n可以通过 /setname 为自己设定名字哦！'
    else:
        nickname = nickname.upper()
    msg = '%s今日人品为%d，%s'
    rp = humanisticCare(
        lambda offset: calcJrrp(
            subject.id if isinstance(subject, Friend) else subject.group.id,
            subject.id, 1 - offset), 1, (5, 50))
    postfix = 'NB！！！'
    if rp == 0:
        postfix = 'SB!!!!'
    elif rp < 50:
        postfix = '不NB，但%sNB！' % ('YD' if nickname != 'YD' else 'TD')
    elif rp < 71:
        postfix = 'NB！'
    elif rp < 100:
        postfix = 'NB！！'
    return MessageChain.create(
        [Plain((msg + postfix) % (nickname, rp, nickname) + hint)])


COMMANDS = {
    'setname': setname_handler,
    'name': name_handler,
    "jrrp": jrrp_handler
}
