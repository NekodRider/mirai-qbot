import logging
import typing as T

from graia.application.friend import Friend
from graia.application.group import Member
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain

from .helper import (args_parser, calcJrrp, getUserInfo, humanisticCare,
                     updateUserInfo)

__all__ = (getUserInfo, updateUserInfo, args_parser)


async def setname_handler(*args, subject: T.Union[Member, Friend]):
    '''设置昵称

    用法: /setname 昵称'''
    if len(args) == 0:
        return MessageChain.create([Plain('使用示例: /setname yd')])
    [name, *_] = args
    oldName = getUserInfo(subject.id)
    try:
        updateUserInfo(subject.id, {'nickname': name})
        return MessageChain.create([
            Plain('成功从' +
                  (oldName['nickname'] if oldName is not None else '-未设定-') +
                  '变更为' + name)
        ])
    except Exception as e:
        logging.exception(e)
        return MessageChain.create([Plain("修改失败qwq")])


async def name_handler(*args, subject: T.Union[Member, Friend]):
    '''显示昵称

    用法: /name'''
    name = getUserInfo(subject.id)
    return MessageChain.create([
        Plain(('你的名字是 ' + name['nickname'] +
               ' ！') if name is not None else '还没设定哦，通过 /setname yd 修改名字~')
    ])


async def jrrp_handler(*args, subject: T.Union[Member, Friend]):
    '''查询今日人品

    用法: /jrrp'''
    if isinstance(subject, Friend):
        return MessageChain.create([Plain("尚未支持该类型")])
    target = getUserInfo(subject.id)

    nickname = subject.name
    hint = ''
    if not target:
        hint = '\n\n可以通过 /setname 为自己设定名字哦！'
    else:
        nickname = target['nickname']

    nickname = nickname.upper()
    msg = '%s今日人品为%d，%s'
    rp = humanisticCare(
        lambda offset: calcJrrp(subject.group.id, subject.id, 1 - offset), 1,
        (5, 50))
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
