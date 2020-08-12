from mirai import Mirai, GroupMessage, Group, MessageChain, Member, Plain
from utils.msg_parser import parseMsg
from mirai.logger import Session as SessionLogger
from mods.users.user_info_loader import getUserInfo, updateUserInfo

sub_app = Mirai(f"mirai://localhost:8080/?authKey=0&qq=0")


def setNameHandler(member: Member, args):
    if len(args) == 0:
        return 'USAGE: /setName yd'
    [name] = args
    oldName = getUserInfo(member.id)
    try:
        updateUserInfo(member.id, {'nickname': name})
        return '成功从' + (oldName['nickname'] if oldName is not None else '-未设定-') + '变更为' + name
    except Exception as err:
        return err


def getNameHandler(member: Member, args):
    name = getUserInfo(member.id)
    return ('你的名字是' + name['nickname'] + '！') if name is not None else '还没设定哦，通过 /setName yd 修改名字~'


# class FUCK:
#     def __init__(self, id = 123123123, n='fuck'):
#         self.id = id
#         self.memberName = n


# a = FUCK()
# setNameHandler(a, ['yd'])
# b = FUCK(121232222, 'fuckyd')

# getNameHandler(b, [])
# setNameHandler(b, ['ydsb'])


USER_CMD_HANDLER = {
    'setname': setNameHandler,
    'name': getNameHandler
}

# cmd = 'rrp'
# if cmd not in FUNNY_CMD_HANDLER.keys():
#     print('fuck')


@sub_app.receiver("GroupMessage")
async def funny_handler(app: Mirai, group: Group, message: MessageChain, member: Member):
    [cmd, *args] = parseMsg(message.toString())
    if cmd not in USER_CMD_HANDLER.keys():
        return
    SessionLogger.info("[USER]群%d中%d消息:" %
                       (group.id, member.id) + cmd + 'args:' + ' '.join(args))
    handler = USER_CMD_HANDLER[cmd]
    msg = [Plain(text=handler(member, args))]
    try:
        await app.sendGroupMessage(group, msg)
    except expression as identifier:
        pass
