from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain

import time

async def help_handler(bot, *args, subject):
    docs = bot.docs
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
        msg = MessageChain.create([Plain(str(res_str + res_str_tail)[:-1])])
    else:
        res_str = ""
        for comm in args:
            comm = bot.prefix + comm if comm[0]!=bot.prefix else comm
            if comm in docs.keys() and type(docs[comm]) == str:
                doc = [x.strip() for x in docs[comm].split("\n")]
                if len(doc)!=3 or doc[0]=="":
                    continue
                res_str += f"{comm[1:]} {doc[2]}\n"
        msg = MessageChain.create([Plain("\n"+res_str[:-1].replace("/",bot.prefix))])

    return msg

async def schedule_handler(bot, *args, subject):
    if len(bot.schedule_task_list)==0:
        return MessageChain.create([Plain("目前没有在运行的任务")])
    res_str = "目前运行的任务有：\n"
    for task in bot.schedule_task_list:
        last_scheduled = task.get('last_scheduled','')
        next_scheduled = task.get('next_scheduled','')
        if last_scheduled!='':
            last_scheduled = time.strftime("%b %d %H:%M:%S",time.localtime(last_scheduled))
        if next_scheduled!='':
            next_scheduled = time.strftime("%b %d %H:%M:%S",time.localtime(next_scheduled))
        res_str += f"{task['name'] if task['name'] else task['func_name']}: {'+'+str(task['interval']) if task['interval'] else task['specific_time']} | {last_scheduled} | {next_scheduled}\n"
    msg = MessageChain.create([Plain(res_str[:-1])])
    return msg


