from graia.application.group import Member
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain
import time


async def help_handler(*args, bot, subject):
    docs = bot.docs
    if len(args) == 0:
        res_str = "目前支持的全部指令有：\n"
        res_str_tail = "其他指令有: "
        for comm, doc in docs.items():
            if type(doc) != str:
                res_str_tail += comm + " "
                continue
            doc = [x.strip() for x in doc.split("\n")]
            if len(doc) != 3 or doc[0] == "":
                res_str_tail += comm + " "
            else:
                res_str += f"{comm}: {doc[0]}\n"
        msg = MessageChain.create([Plain(str(res_str + res_str_tail)[:-1])])
    else:
        res_str = ""
        for comm in args:
            comm = bot.prefix + comm if comm[0] != bot.prefix else comm
            if comm in docs.keys() and type(docs[comm]) == str:
                doc = [x.strip() for x in docs[comm].split("\n")]
                if len(doc) != 3 or doc[0] == "":
                    continue
                res_str += f"{comm[1:]} {doc[2]}\n"
        msg = MessageChain.create(
            [Plain("\n" + res_str[:-1].replace("/", bot.prefix))])

    return msg


async def task_handler(*args, bot, subject):
    if len(bot.schedule_task_list) == 0:
        return MessageChain.create([Plain("目前没有在运行的任务")])
    res_str = "目前运行的任务有：\n"
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
    msg = MessageChain.create([Plain(res_str[:-1])])
    return msg


async def mods_handler(*args, bot, subject):
    target = subject
    if isinstance(subject, Member):
        target = subject.group
    cur_mods = bot.db.get(target, "mods", []).copy()
    all_list = list(bot.commands.keys()).copy()
    if args:
        for keyword in args:
            for mod in bot.commands.keys():
                if keyword not in mod:
                    all_list.remove(mod)
        if all_list:
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
    msg = ""
    target = subject
    if isinstance(subject, Member):
        target = subject.group
    if args[0] == "all":
        for i in bot.commands.keys():
            await bot.subscribe(target, i[len(bot.prefix):])
        msg += "成功启用全部模块.\n"
    else:
        for i in args:
            if bot.prefix + i in bot.commands.keys():
                await bot.subscribe(target, i)
                msg += f"成功启用模块 {i}.\n"
            else:
                msg += f"未找到模块 {i}.\n"
    return MessageChain.create([Plain(msg)])


async def off_handler(*args, bot, subject):
    msg = ""
    target = subject
    if isinstance(subject, Member):
        target = subject.group
    if args[0] == "all":
        for i in bot.commands.keys():
            await bot.unsubscribe(target, i[len(bot.prefix):])
        msg += "成功关闭全部模块.\n"
    else:
        for i in args:
            if bot.prefix + i in bot.commands.keys():
                await bot.unsubscribe(target, i)
                msg += f"成功关闭模块 {i}.\n"
            else:
                msg += f"未找到模块 {i}.\n"
    return MessageChain.create([Plain(msg)])
