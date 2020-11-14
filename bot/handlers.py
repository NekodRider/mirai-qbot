from graia.application.group import Member
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain
from pathlib import Path
import time


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
        res_str = "目前开启的全部模块有：\n"
        res_str_tail = "其他模块有: "
        tail_flag = False
        for comm, doc in docs.items():
            if comm[len(bot.prefix):] not in cur_mods:
                continue
            if type(doc) != str:
                res_str_tail += comm + " "
                continue
            doc = [x.strip() for x in doc.split("\n")]
            if len(doc) != 3 or doc[0] == "":
                tail_flag = True
                res_str_tail += comm + " "
            else:
                res_str += f"{comm}: {doc[0]}\n"
        msg = MessageChain.create(
            [Plain(str(res_str + (res_str_tail if tail_flag else ""))[:-1])])
    else:
        res_str = ""
        for comm in args:
            comm = bot.prefix + comm if comm[:len(bot.prefix
                                                 )] != bot.prefix else comm
            if comm in docs.keys() and type(docs[comm]) == str:
                doc = [x.strip() for x in docs[comm].split("\n")]
                if len(doc) != 3 or doc[0] == "":
                    continue
                res_str += f"{comm[len(bot.prefix):]}({'已启用' if comm[len(bot.prefix):] in cur_mods else '已关闭'}) {doc[2]}\n"
        msg = MessageChain.create(
            [Plain("\n" + res_str[:-1].replace("/", bot.prefix))])

    return msg


async def task_handler(*args, bot, subject):
    '''任务指令
    
    用法: $task'''
    if len(bot.schedule_task_list) == 0:
        return MessageChain.create([Plain("目前没有在运行的任务")])
    res_str = "目前运行的任务和钩子有：\n"
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
        res_str += f"{name}: {func.__doc__}\n"
    msg = MessageChain.create([Plain(res_str[:-1])])
    return msg


async def mods_handler(*args, bot, subject):
    '''命令查询指令
    
    用法: $mods (关键字) 无参数表示查询当前启用模块'''
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
            msg = f"找到模块: {mod_list_str}."
        else:
            msg = f"未找到含有关键字的模块."
    else:
        if cur_mods:
            mod_list_str = str(cur_mods).replace("'", "")
            msg = f"已启用模块: {mod_list_str}."
        else:
            msg = f"未开启任何模块."
    return MessageChain.create([Plain(msg)])


async def on_handler(*args, bot, subject):
    '''启用模块指令
    
    用法: $on 模块名或all'''
    msg = ""
    target = subject
    if isinstance(subject, Member):
        target = subject.group
    if args[0] == "all":
        for i in bot.commands.keys():
            await bot.subscribe(target, i[len(bot.prefix):])
        for i in bot.directs.keys():
            await bot.subscribe(target, i)
        msg += "成功启用全部模块.\n"
    else:
        for i in args:
            if bot.prefix + i in bot.commands.keys() or i in bot.directs.keys():
                await bot.subscribe(target, i)
                msg += f"成功启用模块 {i}.\n"
            else:
                msg += f"未找到模块 {i}.\n"
    return MessageChain.create([Plain(msg)])


async def off_handler(*args, bot, subject):
    '''关闭模块指令
    
    用法: $off 模块名或all'''
    msg = ""
    target = subject
    if isinstance(subject, Member):
        target = subject.group
    if args[0] == "all":
        for i in bot.commands.keys():
            await bot.unsubscribe(target, i[len(bot.prefix):])
        for i in bot.directs.keys():
            await bot.unsubscribe(target, i)
        msg += "成功关闭全部模块.\n"
    else:
        for i in args:
            if bot.prefix + i in bot.commands.keys() or i in bot.directs.keys():
                await bot.unsubscribe(target, i)
                msg += f"成功关闭模块 {i}.\n"
            else:
                msg += f"未找到模块 {i}.\n"
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
