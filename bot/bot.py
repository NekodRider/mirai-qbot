import asyncio
import re
import collections
import importlib
from functools import partial
from re import sub
import time

from pathlib import Path
from typing import Callable, Dict, Any, Union, Tuple
from graia.application import GraiaMiraiApplication, Session
from graia.application.event.lifecycle import ApplicationLaunched, ApplicationShutdowned
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain
from graia.application.group import Group, Member
from graia.application.friend import Friend
from graia.application.message.elements.internal import At
from graia.broadcast import Broadcast
from graia.scheduler import SchedulerTask, Timer
from graia.scheduler.timers import *

from .functions import help_handler, schedule_handler


class Bot(object):
    commands = {}
    schedules = {}
    docs = {}
    app = None
    bcc = None
    logger = None
    prefix = None
    message_queue = asyncio.Queue()
    loop = asyncio.get_event_loop()
    schedule_task_list = []

    def __init__(self, app_configs: Dict, configs: Dict, logger):
        self.commands = {}
        self.bcc = Broadcast(loop=self.loop)
        self.logger = logger
        self.app = GraiaMiraiApplication(
            broadcast=self.bcc,
            connect_info=Session(**app_configs),
            logger=logger
        )
        self.prefix = configs['prefix']
        self.load_mods()

    async def processor(self, interval: int):
        message_queue = self.message_queue
        while True:
            if not message_queue.empty():
                message = await message_queue.get()
                if type(message[0]) == list:
                    msg = message[0]
                else:
                    msg = await message[0](*message[1], **message[2])
                message_queue.task_done()
                try:
                    await self.sendMessage(message[2]["subject"], msg)
                except KeyboardInterrupt:
                    pass
                except Exception as e:
                    self.logger.exception(e)
            await asyncio.sleep(interval)

    def init_processors(self, num: int = 5):
        loop = asyncio.get_event_loop()
        for i in range(1, num + 1):
            loop.create_task(self.processor(i))

    def load_mods(self):
        mod_dir = Path(__file__).parent.parent.joinpath("mods")
        module_prefix = mod_dir.name

        self.commands[self.prefix + "help"] = partial(help_handler, self)
        self.commands[self.prefix + "task"] = partial(schedule_handler, self)
        self.docs[self.prefix + "help"] = f"帮助指令\n\n用法: {self.prefix}help"
        self.docs[self.prefix + "task"] = f"任务指令\n\n用法: {self.prefix}task"

        for mod in mod_dir.iterdir():
            if mod.is_dir() and not mod.name.startswith('_') and mod.joinpath('__init__.py').exists():
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
                        self.commands[comm], self.docs[comm] = func, func.__doc__
            if "SCHEDULES" in dir(mod):
                for name, kwargs in mod.SCHEDULES.items():
                    self.loop.create_task(self.schedule(name, **kwargs))
            self.logger.info(f'成功导入 "{module_path}"')
        except Exception as e:
            self.logger.error(f'未能导入 "{module_path}", error: {e}')
            self.logger.exception(e)

    async def sendMessage(self, subject: Union[Tuple[str, int], Group, Member, Friend], msg: MessageChain):
        if isinstance(subject, Member):
            new_msg = MessageChain.create([At(subject.id)])
            new_msg.plus(msg)
            await self.app.sendGroupMessage(subject.group, new_msg)
        elif isinstance(subject, Group):
            await self.app.sendGroupMessage(subject, msg)
        elif isinstance(subject, Friend):
            await self.app.sendFriendMessage(subject, msg)
        elif isinstance(subject, tuple):
            if subject[0] == "Friend":
                await self.app.sendFriendMessage(subject[1], msg)
            else:
                await self.app.sendGroupMessage(subject[1], msg)
        pass

    async def judge(self, subject: Union[Member, Friend], message: MessageChain):
        try:
            message_str = message.asDisplay()
            pattern = self.prefix + r"([\S]+ )*[\S]+"
            match = re.match(pattern, message_str, re.I)
            command_str = ""
            if match:
                command_str = message_str[match.span()[0]:match.span()[
                    1]].lower()
                [comm, *args] = command_str.split(" ")
                if comm in self.commands.keys():
                    if isinstance(subject, Member):
                        self.logger.info(
                            f"[{comm[len(self.prefix):]}]来自群{subject.group.id}中成员{subject.id}的指令:" + message_str)
                    else:
                        self.logger.info(
                            f"[{comm[len(self.prefix):]}]来自好友{subject.id}的指令:" + message_str)
                    await self.message_queue.put((self.commands[comm], args, {"subject": subject}))
        except KeyboardInterrupt:
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

    async def schedule(self, name: str, func: Callable[..., Any], interval: int = None, specific_time: str = None):
        if not interval and not specific_time:
            self.logger.error(f"{name} 计划任务未指定时间，已忽略！")
            return
        tmp = {"name": name, "func_name": func.__name__,
               "interval": interval, "specific_time": specific_time}
        self.schedule_task_list.append(tmp)
        index = self.schedule_task_list.index(tmp)

        async def wrapper():
            self.schedule_task_list[index]["last_scheduled"] = time.time()
            self.schedule_task_list[index]["next_scheduled"] = time.time(
            ) + (interval or 24*60*60)
            await partial(func, self)()

        if interval:
            timer = every_custom_seconds(interval)
            next_call = datetime.now() + timedelta(seconds=interval)
            self.schedule_task_list[index]["next_scheduled"] = datetime.timestamp(
                next_call)
        else:
            h, m, s = [int(specific_time[2*i:2*i+2]) for i in range(3)]
            next_call = datetime.now().replace(hour=h, minute=m, second=s)
            if next_call < datetime.now():
                next_call += timedelta(hours=24)
            self.schedule_task_list[index]["next_scheduled"] = datetime.timestamp(
                next_call)
            remain = datetime.timestamp(next_call) - time.time()
            await asyncio.sleep(remain)
            await wrapper()
            timer = every_custom_hours(24)

        t = SchedulerTask(wrapper, timer, self.bcc,
                          self.loop, logger=self.logger)

        t.setup_task()
