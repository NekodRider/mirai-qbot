import re
import importlib
import collections
import asyncio
from pathlib import Path
from threading import Lock
from mirai import Mirai, exceptions, MessageChain, Group, At, Friend, Member, Plain
from mirai.logger import Session as SessionLogger
from ._utils import Sender, Type

PREFIX = ""
commands = {}
docs = {}
message_queue = []
MQ_LOCK = Lock()
sub_app = Mirai(f"mirai://localhost:8080/?authKey=0&qq=0")

async def help_handler(*args,sender, event_type):
    res_str = "目前支持的指令有：\n"
    res_str_tail = "其他指令有: "
    global docs
    docs = collections.OrderedDict(sorted(docs.items()))
    for comm, doc in docs.items():
        if doc != "":
            res_str += f"{comm}: {doc}\n"
        else:
            res_str_tail += comm + " "
    msg = [Plain(text=(res_str + res_str_tail)[:-1])]
    return msg

def load_mods(app: Mirai, prefix: str):
    global PREFIX
    PREFIX = prefix
    mod_dir = Path(__file__).parent
    module_prefix = mod_dir.name

    commands[PREFIX + "help"] = help_handler
    docs[PREFIX + "help"] = ""

    for mod in mod_dir.iterdir():
        if mod.is_dir() and not mod.name.startswith('_') and mod.joinpath('__init__.py').exists():
            load_mod(app, f'{module_prefix}.{mod.name}')


def load_mod(app: Mirai, module_path: str):
    try:
        mod = importlib.import_module(module_path)
        if "COMMANDS" in dir(mod):
            for comm, func_doc in mod.COMMANDS.items():
                comm = PREFIX + comm
                if comm in commands.keys():
                    SessionLogger.error(f'未能导入 "{module_path}", error: 已存在指令{comm}')
                else:
                    commands[comm], docs[comm] = func_doc
        SessionLogger.info(f'成功导入 "{module_path}"')
    except Exception as e:
        SessionLogger.error(f'未能导入 "{module_path}", error: {e}')
        SessionLogger.exception(e)


@sub_app.receiver("FriendMessage")
@sub_app.receiver("GroupMessage")
async def command_handler(app: Mirai, sender: "Sender", event_type: "Type", message: MessageChain):
    message_str = message.toString()
    pattern = PREFIX + "([a-z0-9.]+ )*[a-z0-9.]+"
    match = re.match(pattern,message_str,re.I)
    command_str = ""
    if match:
        command_str = message_str[match.span()[0]:match.span()[1]].lower()
        [comm,*args] = command_str.split(" ")
        if comm in commands.keys():
            if event_type == "GroupMessage":
                SessionLogger.info(f"[{comm[len(PREFIX):]}]来自群{sender.group.id}中成员{sender.id}的指令:" + message_str)
            elif event_type == "FriendMessage":
                SessionLogger.info(f"[{comm[len(PREFIX):]}]来自好友{sender.id}的指令:" + message_str)
            else:
                SessionLogger.error(f"未知事件类型{event_type}")
                return
            MQ_LOCK.acquire()
            message_queue.append((commands[comm],args,{"sender":sender,"event_type":event_type}))
            MQ_LOCK.release()

async def processor(app: Mirai, interval: int):
    global message_queue
    while 1:
        if len(message_queue)!=0:
            MQ_LOCK.acquire()
            message = message_queue[0]
            message_queue = message_queue[1:]
            MQ_LOCK.release()
            msg = await message[0](*message[1],**message[2])
            try:
                if message[2]["event_type"] == "FriendMessage":
                    await app.sendFriendMessage(message[2]["sender"].id, msg)
                elif message[2]["event_type"] == "GroupMessage":
                    msg.insert(0, At(message[2]["sender"].id))
                    await app.sendGroupMessage(message[2]["sender"].group, msg)
                else:
                    SessionLogger.error(f"未知事件类型{message[2]['event_type']}")
            except exceptions.BotMutedError:
                pass
        await asyncio.sleep(interval)

def init_processor(app: Mirai, num: int = 5):
    loop = asyncio.get_event_loop()
    for i in range(1, num + 1):
        loop.create_task(processor(app, i))