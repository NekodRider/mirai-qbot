import re
import importlib
import collections
import asyncio
from pathlib import Path
from queue import Queue
from mirai import Mirai, exceptions, MessageChain, Group, At, Friend, Member, Plain
from mirai.logger import Session as SessionLogger
from ._utils import Sender, Type
from ._utils.decorator import schedule_task_list

sub_app = Mirai(f"mirai://localhost:8080/?authKey=0&qq=0")

PREFIX = ""
commands = {}
docs = {}
message_queue = Queue()

async def help_handler(*args,sender, event_type):
    global docs
    if len(args)==0:
        res_str = "目前支持的指令有：\n"
        res_str_tail = "其他指令有: "
        for comm, doc in docs.items():
            if type(doc)!=str:
                res_str_tail += comm + " "
                continue
            doc = [x.strip() for x in doc.split("\n")]
            if len(doc)!=3 or doc[0]=="":
                res_str_tail += comm + " "
            else:
                res_str += f"{comm}: {doc[0]}\n"
        msg = [Plain(text=(res_str + res_str_tail)[:-1])]
    else:
        res_str = ""
        for comm in args:
            comm = PREFIX + comm if comm[0]!=PREFIX else comm
            if comm in docs.keys() and type(docs[comm]) == str:
                doc = [x.strip() for x in docs[comm].split("\n")]
                if len(doc)!=3 or doc[0]=="":
                    continue
                res_str += f"{comm[1:]} {doc[2]}\n"
        msg = [Plain(text="\n"+res_str[:-1].replace("/",PREFIX))]

    return msg

async def schedule_handler(*args,sender, event_type):
    res_str = "目前运行的任务有：\n"
    for task in schedule_task_list:
        res_str += f"{task['name'] if task['name'] else task['func_name']}: {'+'+task['interval'] if task['interval'] else task['specific_time']} | {task['last_scheduled']} | {task['next_scheduled']}\n"
    msg = [Plain(text=res_str[:-1])]
    return msg

def load_mods(app: Mirai, prefix: str):
    global PREFIX, docs
    PREFIX = prefix
    mod_dir = Path(__file__).parent
    module_prefix = mod_dir.name

    commands[PREFIX + "help"] = help_handler
    commands[PREFIX + "task"] = schedule_handler
    docs[PREFIX + "help"] = f"帮助指令\n\n用法: {PREFIX}help"
    docs[PREFIX + "task"] = f"任务指令\n\n用法: {PREFIX}task"

    for mod in mod_dir.iterdir():
        if mod.is_dir() and not mod.name.startswith('_') and mod.joinpath('__init__.py').exists():
            load_mod(app, f'{module_prefix}.{mod.name}')
    
    docs = collections.OrderedDict(sorted(docs.items()))


def load_mod(app: Mirai, module_path: str):
    try:
        mod = importlib.import_module(module_path)
        if "COMMANDS" in dir(mod):
            for comm, func in mod.COMMANDS.items():
                comm = PREFIX + comm
                if comm in commands.keys():
                    SessionLogger.error(f'未能导入 "{module_path}", error: 已存在指令{comm}')
                else:
                    commands[comm], docs[comm] = func, func.__doc__
        SessionLogger.info(f'成功导入 "{module_path}"')
    except Exception as e:
        SessionLogger.error(f'未能导入 "{module_path}", error: {e}')
        SessionLogger.exception(e)


@sub_app.receiver("FriendMessage")
@sub_app.receiver("GroupMessage")
async def command_handler(app: Mirai, sender: "Sender", event_type: "Type", message: MessageChain):
    message_str = message.toString()
    pattern = PREFIX + r"([\S]+ )*[\S]+"
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
            message_queue.put((commands[comm],args,{"sender":sender,"event_type":event_type}))
        # 因为较新的表情均为 /头秃 等形式与指令冲突, 暂时取消这个功能
        # else:
        #     msg = [Plain(text=f"未知命令 {comm}")]
        #     try:
        #         if event_type == "FriendMessage":
        #             await app.sendFriendMessage(sender.id, msg)
        #         elif event_type == "GroupMessage":
        #             msg.insert(0, At(sender.id))
        #             await app.sendGroupMessage(sender.group, msg)
        #         else:
        #             SessionLogger.error(f"未知事件类型{event_type}")
        #     except exceptions.BotMutedError:
        #         pass

async def processor(app: Mirai, interval: int):
    global message_queue
    while 1:
        if not message_queue.empty():
            message = message_queue.get()
            if type(message[0]) == list:
                msg = message[0]
            else:
                msg = await message[0](*message[1],**message[2])
            message_queue.task_done()
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