from mirai import Mirai, GroupMessage, Group, MessageChain, Member, Plain, exceptions
from .._utils import parseMsg
from mirai.logger import Session as SessionLogger
from .user_info_loader import getUserInfo, updateUserInfo

__all__ = ["getUserInfo", "updateUserInfo"]

async def setname_handler(*args,sender,event_type):
    if len(args) == 0:
        return [Plain(text='USAGE: /setname yd')]
    [name, *_] = args
    oldName = getUserInfo(sender.id)
    try:
        updateUserInfo(sender.id, {'nickname': name})
        return [Plain(text='成功从' + (oldName['nickname'] if oldName is not None else '-未设定-') + '变更为' + name)]
    except Exception:
        return [Plain(text="修改失败qwq")]

async def name_handler(*args,sender,event_type):
    name = getUserInfo(sender.id)
    return [Plain(text=('你的名字是 ' + name['nickname'] + ' ！') if name is not None else '还没设定哦，通过 /setname yd 修改名字~')]

COMMANDS = {
    'setname': (setname_handler, "设置昵称"),
    'name': (name_handler, "显示昵称")
}
