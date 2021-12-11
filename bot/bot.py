#type: ignore
import asyncio
import collections
import importlib
import re
import time
from functools import lru_cache, partial
from logging import DEBUG, handlers
from pathlib import Path
from queue import Queue
from re import sub
from threading import Thread
from typing import Any, Callable, Dict, List, Tuple, Union

import aiohttp
from graia.application import GraiaMiraiApplication, Session, logger
from graia.application.event.lifecycle import (ApplicationLaunched,
                                               ApplicationShutdowned)
from graia.application.friend import Friend
from graia.application.group import Group, Member, MemberPerm
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import At, Plain
from graia.broadcast import Broadcast
from graia.scheduler import SchedulerTask, Timer
from graia.scheduler.timers import *

from .db import Storage
from .handlers import INNER_COMMANDS
from .logger import DefaultLogger, defaultLogger


class Bot(object):

    def __init__(self, app_configs: Dict, configs: Dict):
        self.directs = {}
        self.docs = {}
        self.schedules = {}
        self.inner_commands = {}
        self.commands = {}
        self.schedule_task_list = []
        self.message_queue = Queue()
        self.command_queue = Queue()
        self.history = None
        self.loop = asyncio.get_event_loop()
        self.bcc = Broadcast(loop=self.loop)
        self.counters = [0, 0]
        if configs['debug']:
            global defaultLogger
            defaultLogger.close()
            defaultLogger = DefaultLogger(level=DEBUG)
        self.logger = defaultLogger
        self.app = GraiaMiraiApplication(broadcast=self.bcc,
                                         connect_info=Session(**app_configs),
                                         logger=self.logger,
                                         debug=configs['debug'])
        self.prefix = configs['prefix']
        self.db = Storage.load()
        self.load_mods()

    async def processor(self):
        self.counters[0] += 1
        while True:
            command_queue = self.command_queue
            if not command_queue.empty():
                message = command_queue.get()
                if type(message[0]) == list:
                    msg = message[0]
                else:
                    try:
                        msg = await message[0](*message[1], **message[2])
                    except KeyboardInterrupt or SystemExit:
                        self.counters[0] -= 1
                        return
                    except Exception as e:
                        self.counters[0] -= 1
                        self.logger.exception(e)
                        self.init_processors(1)
                        return
                command_queue.task_done()
                self.message_queue.put((message[2]["subject"], msg))
            await asyncio.sleep(1)

    async def sender(self):
        self.counters[1] += 1
        while True:
            message_queue = self.message_queue
            if not message_queue.empty():
                subject, msg = self.message_queue.get()
                try:
                    await self.sendMessage(subject, msg)
                except KeyboardInterrupt or SystemExit:
                    self.counters[1] -= 1
                    return
                except Exception as e:
                    self.counters[1] -= 1
                    self.logger.exception(e)
                    return
            await asyncio.sleep(1)

    def init_processors(self, num: int = 5):

        def start_loop(loop):
            asyncio.set_event_loop(loop)
            loop.run_forever()

        for _ in range(1, num + 1):
            sub_loop = asyncio.new_event_loop()
            sub_thread = Thread(target=start_loop, args=(sub_loop,))
            sub_thread.setDaemon(True)
            sub_thread.start()
            asyncio.run_coroutine_threadsafe(self.processor(), sub_loop)
            self.loop.create_task(self.sender())

    def load_mods(self):
        self.docs["内置"] = [{}, {}]
        for comm, func in INNER_COMMANDS.items():
            comm = self.prefix + comm
            self.inner_commands[comm], self.docs["内置"][0][
                comm] = func, func.__doc__.replace("$", self.prefix)

        mod_dir = Path(__file__).parent.parent.joinpath("mods")
        module_prefix = mod_dir.name

        mod_count = 0
        for mod in mod_dir.iterdir():
            if mod.is_dir() and not mod.name.startswith('_') and mod.joinpath(
                    '__init__.py').exists():
                module_path = f'{module_prefix}.{mod.name}'
                try:
                    m = importlib.import_module(module_path)
                    module_name = m.NAME if "NAME" in dir(m) else mod.name
                    self.docs[module_name] = [{}, {}]
                    if "COMMANDS" in dir(m):
                        for comm, func in m.COMMANDS.items():
                            comm = self.prefix + comm
                            if comm in self.commands.keys(
                            ) or comm in self.inner_commands.keys():
                                self.logger.error(
                                    f'未能导入 "{module_path}", error: 已存在指令{comm}')
                            else:
                                self.commands[comm], self.docs[module_name][0][
                                    comm] = func, func.__doc__
                    if "SCHEDULES" in dir(m):
                        for name, kwargs in m.SCHEDULES.items():
                            self.loop.create_task(self.schedule(name, **kwargs))
                    if "DIRECTS" in dir(m):
                        for name, func in m.DIRECTS.items():
                            self.directs[name], self.docs[module_name][1][
                                name] = func, func.__doc__
                    mod_count += 1
                    self.logger.debug(f'成功导入 "{module_path}"')
                except Exception as e:
                    self.logger.error(f'未能导入 "{module_path}", error: {e}')
                    self.logger.exception(e)

        self.logger.info(f'成功导入 {mod_count} 个模组.')

    async def simpleRecallLastMessage(self):
        await self.app.revokeMessage(self.history)

    async def sendMessage(self,
                          subject: Union[Tuple[str, int], Group, Member,
                                         Friend],
                          msg: MessageChain,
                          withAt=True):
        try:
            if isinstance(subject, Member):
                if not withAt:
                    ret = await self.app.sendGroupMessage(subject.group, msg)
                else:
                    new_msg = MessageChain.create([At(subject.id)
                                                  ]).plusWith(msg)
                    ret = await self.app.sendGroupMessage(
                        subject.group, new_msg)
            if isinstance(subject, Group):
                ret = await self.app.sendGroupMessage(subject, msg)
            elif isinstance(subject, Friend):
                ret = await self.app.sendFriendMessage(subject, msg)
            elif isinstance(subject, tuple):
                if subject[0] == "Friend":
                    ret = await self.app.sendFriendMessage(subject[1], msg)
                else:
                    ret = await self.app.sendGroupMessage(subject[1], msg)
            self.history = ret
        except KeyboardInterrupt or SystemExit:
            pass
        except Exception as e:
            self.logger.exception(e)

    async def judge(self, subject: Union[Member, Friend],
                    message: MessageChain):
        try:
            if isinstance(subject, Member):
                cur_mods = self.db.get(subject.group, "mods", [])
            else:
                cur_mods = self.db.get(subject, "mods", [])
            for name, direct in self.directs.items():
                if name in cur_mods:
                    asyncio.create_task(direct(message, self, subject))
            message_str = message.asDisplay()
            pattern = self.prefix + r"([\S]+ )*[\S]+"
            match = re.match(pattern, message_str, re.I)
            command_str = ""
            if match:
                command_str = message_str[match.span()[0]:match.span(
                )[1]].lower()
                [comm, *args] = command_str.split(" ")
                if isinstance(subject, Member):
                    text = f"[{comm[len(self.prefix):]}]来自群{subject.group.id}中成员{subject.id}的指令:"
                else:
                    text = f"[{comm[len(self.prefix):]}]来自好友{subject.id}的指令:"
                if comm in self.inner_commands.keys():
                    self.logger.info(text + message_str)
                    self.command_queue.put((self.inner_commands[comm], args, {
                        "bot": self,
                        "subject": subject
                    }))
                elif comm in self.commands.keys():
                    if comm[len(self.prefix):] in cur_mods:
                        self.logger.info(text + message_str)
                        self.command_queue.put((self.commands[comm], args, {
                            "bot": self,
                            "subject": subject
                        }))
                    else:
                        await self.sendMessage(
                            subject,
                            MessageChain.create([
                                Plain(
                                    f"未启用 {comm[len(self.prefix):]}, 可通过输入/on {comm[len(self.prefix):]} 来启用命令。"
                                )
                            ]))

        except KeyboardInterrupt or SystemExit:
            pass
        except Exception as e:
            self.logger.exception(e)

    def activate(self):

        @self.bcc.receiver("GroupMessage")
        async def _(member: Member, message: MessageChain):
            await self.judge(member, message)

        @self.bcc.receiver("FriendMessage")
        async def _(friend: Friend, message: MessageChain):
            await self.judge(friend, message)

        try:
            self.init_processors()
            self.app.launch_blocking()
        except KeyboardInterrupt or SystemExit:
            return

    async def schedule(self,
                       name: str,
                       func: Callable[..., Any],
                       interval: int = None,
                       specific_time: str = None):
        if not interval and not specific_time:
            self.logger.error(f"{name} 计划任务未指定时间，已忽略！")
            return
        tmp = {
            "name": name,
            "func_name": func.__name__,
            "interval": interval,
            "specific_time": specific_time
        }
        self.schedule_task_list.append(tmp)
        index = self.schedule_task_list.index(tmp)

        async def wrapper():
            self.schedule_task_list[index]["last_scheduled"] = time.time()
            self.schedule_task_list[index]["next_scheduled"] = time.time() + (
                interval or 24 * 60 * 60)
            await partial(func, self)()

        if interval:
            timer = every_custom_seconds(interval)
            next_call = datetime.now() + timedelta(seconds=interval)
            self.schedule_task_list[index][
                "next_scheduled"] = datetime.timestamp(next_call)
        else:
            h, m, s = [int(specific_time[2 * i:2 * i + 2]) for i in range(3)]
            next_call = datetime.now().replace(hour=h, minute=m, second=s)
            if next_call < datetime.now():
                next_call += timedelta(hours=24)
            self.schedule_task_list[index][
                "next_scheduled"] = datetime.timestamp(next_call)
            remain = datetime.timestamp(next_call) - time.time()
            await asyncio.sleep(remain)
            await wrapper()
            timer = every_custom_hours(24)

        t = SchedulerTask(wrapper, timer, self.bcc, self.loop)

        t.setup_task()

    async def subscribe(self, subject: Union[Group, Friend], mod: str):
        self.db.set(subject, {"mods": [mod]})

    async def unsubscribe(self, subject: Union[Group, Friend], mod: str):
        cur_mods = self.db.get(subject, "mods", [])
        if cur_mods and mod in cur_mods:
            cur_mods.remove(mod)
        self.db.set(subject, {"mods": cur_mods}, replace=True)

    async def subscriberByMod(self, mods: List):
        res = {"friends": [], "groups": []}
        for friend in self.db.friends.keys():
            if all([
                    x in self.db.get(Friend(id=friend, nickname="", remark=""),
                                     "mods", []) for x in mods
            ]):
                res["friends"].append(friend)
        for group in self.db.groups.keys():
            if all([
                    x in self.db.get(
                        Group(id=group, name="", permission=MemberPerm.Member),
                        "mods", []) for x in mods
            ]):
                res["groups"].append(group)
        return res
