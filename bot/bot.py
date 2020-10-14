#type: ignore
import asyncio
import collections
import importlib
import re
import time
from functools import partial
from pathlib import Path
from queue import Queue
from threading import Thread
from typing import Any, Callable, Dict, Tuple, Union
from logging import DEBUG

from graia.application import GraiaMiraiApplication, Session
from graia.application.event.lifecycle import (ApplicationLaunched,
                                               ApplicationShutdowned)
from graia.application.friend import Friend
from graia.application.group import Group, Member
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import At, Plain
from graia.broadcast import Broadcast
from graia.scheduler import SchedulerTask, Timer
from graia.scheduler.timers import *

from .functions import help_handler, schedule_handler
from .logger import defaultLogger, DefaultLogger


class Bot(object):
    directs = {}
    commands = {}
    schedules = {}
    docs = {}
    app = None
    bcc = None
    logger = None
    prefix = None
    message_queue = Queue()
    command_queue = Queue()
    loop = asyncio.get_event_loop()
    schedule_task_list = []

    def __init__(self, app_configs: Dict, configs: Dict):
        self.commands = {}
        self.bcc = Broadcast(loop=self.loop)
        if configs['debug']:
            global defaultLogger
            defaultLogger.close()
            defaultLogger = DefaultLogger(level=DEBUG)
        self.logger = defaultLogger
        self.app = GraiaMiraiApplication(broadcast=self.bcc,
                                         connect_info=Session(**app_configs),
                                         logger=self.logger)
        self.prefix = configs['prefix']
        self.load_mods()

    async def processor(self):
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
                        return
                    except Exception as e:
                        self.logger.exception(e)
                        return
                command_queue.task_done()
                self.message_queue.put((message[2]["subject"], msg))
            await asyncio.sleep(1)

    async def sender(self):
        while True:
            message_queue = self.message_queue
            if not message_queue.empty():
                subject, msg = self.message_queue.get()
                try:
                    await self.sendMessage(subject, msg)
                except KeyboardInterrupt or SystemExit:
                    return
                except Exception as e:
                    self.logger.exception(e)
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
        mod_dir = Path(__file__).parent.parent.joinpath("mods")
        module_prefix = mod_dir.name

        self.commands[self.prefix + "help"] = partial(help_handler, self)
        self.commands[self.prefix + "task"] = partial(schedule_handler, self)
        self.docs[self.prefix + "help"] = f"帮助指令\n\n用法: {self.prefix}help"
        self.docs[self.prefix + "task"] = f"任务指令\n\n用法: {self.prefix}task"

        for mod in mod_dir.iterdir():
            if mod.is_dir() and not mod.name.startswith('_') and mod.joinpath(
                    '__init__.py').exists():
                self.load_mod(f'{module_prefix}.{mod.name}')

        self.docs = collections.OrderedDict(sorted(self.docs.items()))

    def load_mod(self, module_path: str):
        try:
            mod = importlib.import_module(module_path)
            if "COMMANDS" in dir(mod):
                for comm, func in mod.COMMANDS.items():
                    comm = self.prefix + comm
                    if comm in self.commands.keys():
                        self.logger.error(
                            f'未能导入 "{module_path}", error: 已存在指令{comm}')
                    else:
                        self.commands[comm], self.docs[
                            comm] = func, func.__doc__
            if "SCHEDULES" in dir(mod):
                for name, kwargs in mod.SCHEDULES.items():
                    self.loop.create_task(self.schedule(name, **kwargs))
            if "DIRECTS" in dir(mod):
                for name, func in mod.DIRECTS.items():
                    self.directs[name], self.docs[name] = func, func.__doc__
            self.logger.info(f'成功导入 "{module_path}"')
        except Exception as e:
            self.logger.error(f'未能导入 "{module_path}", error: {e}')
            self.logger.exception(e)

    async def sendMessage(self, subject: Union[Tuple[str, int], Group, Member,
                                               Friend], msg: MessageChain):
        if isinstance(subject, Member):
            new_msg = MessageChain.create([At(subject.id)])
            new_msg.plus(msg)
            await self.app.sendGroupMessage(subject.group, new_msg)
        if isinstance(subject, Group):
            await self.app.sendGroupMessage(subject, msg)
        elif isinstance(subject, Friend):
            await self.app.sendFriendMessage(subject, msg)
        elif isinstance(subject, tuple):
            if subject[0] == "Friend":
                await self.app.sendFriendMessage(subject[1], msg)
            else:
                await self.app.sendGroupMessage(subject[1], msg)
        pass

    async def judge(self, subject: Union[Member, Friend],
                    message: MessageChain):
        try:
            for direct in self.directs.values():
                asyncio.create_task(direct(self, message, subject))
            message_str = message.asDisplay()
            pattern = self.prefix + r"([\S]+ )*[\S]+"
            match = re.match(pattern, message_str, re.I)
            command_str = ""
            if match:
                command_str = message_str[match.span()[0]:match.span(
                )[1]].lower()
                [comm, *args] = command_str.split(" ")
                if comm in self.commands.keys():
                    if isinstance(subject, Member):
                        self.logger.info(
                            f"[{comm[len(self.prefix):]}]来自群{subject.group.id}中成员{subject.id}的指令:"
                            + message_str)
                    else:
                        self.logger.info(
                            f"[{comm[len(self.prefix):]}]来自好友{subject.id}的指令:" +
                            message_str)
                    self.command_queue.put((self.commands[comm], args, {
                        "subject": subject
                    }))
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

        t = SchedulerTask(wrapper,
                          timer,
                          self.bcc,
                          self.loop,
                          logger=self.logger)

        t.setup_task()
