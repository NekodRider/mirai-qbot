from mirai import Mirai, GroupMessage, Group, MessageChain, Member, Plain
from mirai.logger import Session as SessionLogger
from utils.msg_parser import parseMsg
from mods.funny.jrrp import jrrpHandler

sub_app = Mirai(f"mirai://localhost:8080/?authKey=0&qq=0")

FUNNY_CMD_HANDLER = {
    'jrrp': jrrpHandler
}

# cmd = 'rrp'
# if cmd not in FUNNY_CMD_HANDLER.keys():
#     print('fuck')


@sub_app.receiver("GroupMessage")
async def funny_handler(app: Mirai, group: Group, message: MessageChain, member: Member):
    [cmd, *args] = parseMsg(message.toString())
    if cmd not in FUNNY_CMD_HANDLER.keys():
        return
    SessionLogger.info("[FUNNY]群%d中%d消息:" %
                       (group.id, member.id)  + cmd + ' ' + ' '.join(args))
    handler = FUNNY_CMD_HANDLER[cmd]
    msg = [Plain(text=handler(group, member, args))]
    try:
        await app.sendGroupMessage(group, msg)
    except expression as identifier:
        pass
