import time
from pathlib import Path

from graia.application.group import Member
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain


async def help_handler(*args, bot, subject):
    '''帮助指令
    
    用法: $help'''
    docs = bot.docs
    target = subject
    if isinstance(subject, Member):
        target = subject.group
    cur_mods = bot.db.get(target, "mods", []) + [
        i[len(bot.prefix):] for i in bot.inner_commands.keys()
    ]
    if len(args) == 0:
        res_str = ""
        for comms, kv in docs.items():
            res_str += f"{comms} 模块:\n"
            for comm, doc in kv[0].items():
                if isinstance(doc, str):
                    doc = [x.strip() for x in doc.split("\n")]
                    if len(doc) == 3 and doc[0] != "":
                        res_str += f"- {comm}: {doc[0]}\n"
                        continue
                res_str += f"- {comm}\n"
            for comm, doc in kv[1].items():
                if isinstance(doc, str):
                    doc = [x.strip() for x in doc.split("\n")]
                    if len(doc) == 3 and doc[0] != "":
                        res_str += f"- {comm}: {doc[0]}\n"
                        continue
                res_str += f"- {comm}\n"
        msg = MessageChain.create([Plain(str(res_str[:-1]))])
    else:
        res_str = ""
        pre_args = [
            bot.prefix + comm if comm[:len(bot.prefix)] != bot.prefix else comm
            for comm in args
        ]
        for comms, kv in docs.items():
            for comm, doc in kv[1].items():
                if comm in args and type(doc) == str:
                    doc = [x.strip() for x in doc.split("\n")]
                    if len(doc) != 3 or doc[0] == "":
                        continue
                    res_str += f"{comm[len(bot.prefix):]}({'已启用' if comm[len(bot.prefix):] in cur_mods else '已关闭'}) {doc[2]}\n"

            for comm, doc in kv[0].items():
                if comm in pre_args and type(doc) == str:
                    doc = [x.strip() for x in doc.split("\n")]
                    if len(doc) != 3 or doc[0] == "":
                        continue
                    res_str += f"{comm[len(bot.prefix):]}({'已启用' if comm[len(bot.prefix):] in cur_mods else '已关闭'}) {doc[2]}\n"
        msg = MessageChain.create(
            [Plain(res_str[:-1].replace("/", bot.prefix))])

    return msg


async def task_handler(*args, bot, subject):
    '''任务指令
    
    用法: $task'''
    counters = f"当前有 {bot.counters[0]} 个 worker, {bot.counters[1]} 个 sender\n"
    if len(bot.schedule_task_list) == 0:
        return MessageChain.create([Plain(counters + "目前没有在运行的任务.")])
    res_str = counters + "目前运行的任务和钩子有：\n"
    for task in bot.schedule_task_list:
        last_scheduled = task.get('last_scheduled', '')
        next_scheduled = task.get('next_scheduled', '')
        if last_scheduled != '':
            last_scheduled = time.strftime("%b %d %H:%M:%S",
                                           time.localtime(last_scheduled))
        if next_scheduled != '':
            next_scheduled = time.strftime("%b %d %H:%M:%S",
                                           time.localtime(next_scheduled))
        res_str += f"{task['name'] if task['name'] else task['func_name']}: {'+'+str(task['interval']) if task['interval'] else task['specific_time']} | {last_scheduled} | {next_scheduled}\n"
    for name, func in bot.directs.items():
        doc = func.__doc__.split('\n')[0]
        res_str += f"{name}: {doc}\n"
    msg = MessageChain.create([Plain(res_str[:-1])])
    return msg


async def mods_handler(*args, bot, subject):
    '''命令查询指令
    
    用法: $mods (关键字) 无参数表示查询当前启用命令'''
    target = subject
    if isinstance(subject, Member):
        target = subject.group
    cur_mods = bot.db.get(target, "mods", []).copy()
    all_list = [i[len(bot.prefix):] for i in list(bot.commands.keys())] + list(
        bot.directs.keys())
    if args:
        for keyword in args:
            if keyword == "all" or keyword == "*":
                break
            all_list = list(filter(lambda a: keyword in a, all_list))
        if all_list:
            for i in range(len(all_list)):
                all_list[
                    i] = f"{all_list[i]}: {'on' if all_list[i] in cur_mods else 'off'}"
            mod_list_str = str(all_list).replace("'", "")
            msg = f"找到命令: {mod_list_str}."
        else:
            msg = f"未找到含有关键字的命令."
    else:
        if cur_mods:
            mod_list_str = str(cur_mods).replace("'", "")
            msg = f"已启用命令: {mod_list_str}."
        else:
            msg = f"未开启任何命令."
    return MessageChain.create([Plain(msg)])


async def on_handler(*args, bot, subject):
    '''启用命令指令
    
    用法: $on 命令名或all'''
    msg = ""
    target = subject
    if isinstance(subject, Member):
        target = subject.group
    if args[0] == "all":
        for i in bot.commands.keys():
            await bot.subscribe(target, i[len(bot.prefix):])
        for i in bot.directs.keys():
            await bot.subscribe(target, i)
        msg += "成功启用全部命令.\n"
    else:
        for i in args:
            if bot.prefix + i in bot.commands.keys() or i in bot.directs.keys():
                await bot.subscribe(target, i)
                msg += f"成功启用命令 {i}.\n"
            else:
                msg += f"未找到命令 {i}.\n"
    return MessageChain.create([Plain(msg)])


async def off_handler(*args, bot, subject):
    '''关闭命令指令
    
    用法: $off 命令名或all'''
    msg = ""
    target = subject
    if isinstance(subject, Member):
        target = subject.group
    if args[0] == "all":
        for i in bot.commands.keys():
            await bot.unsubscribe(target, i[len(bot.prefix):])
        for i in bot.directs.keys():
            await bot.unsubscribe(target, i)
        msg += "成功关闭全部命令.\n"
    else:
        for i in args:
            if bot.prefix + i in bot.commands.keys() or i in bot.directs.keys():
                await bot.unsubscribe(target, i)
                msg += f"成功关闭命令 {i}.\n"
            else:
                msg += f"未找到命令 {i}.\n"
    return MessageChain.create([Plain(msg)])


async def logger_handler(*args, bot, subject):
    '''日志查询指令
    
    用法: $log'''
    with open(Path(__file__).parent.parent.joinpath("logs", "mirai_bot.log"),
              "r",
              encoding='utf-8') as f:
        res = f.readlines()
        res = "".join(res[0 if len(res) < 21 else len(res) - 21:len(res) - 1])
    return MessageChain.create([Plain(res)])


INNER_COMMANDS = {
    "help": help_handler,
    "task": task_handler,
    "mods": mods_handler,
    "on": on_handler,
    "off": off_handler,
    "log": logger_handler
}
