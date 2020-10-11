import typing as T
import asyncio
import re
import collections
import importlib
from functools import partial

from pathlib import Path
from graia.application import GraiaMiraiApplication, Session
from graia.application.event.lifecycle import ApplicationLaunched, ApplicationShutdowned
from graia.application.message.chain import MessageChain
from graia.application.group import Group, Member
from graia.application.friend import Friend
from graia.broadcast import Broadcast

from .functions import *

loop = asyncio.get_event_loop()

class Bot(object):
    commands = {}
    docs = {}
    app = None
    bcc = None
    logger = None
    prefix = None
    message_queue = asyncio.Queue()
    schedule_task_list = []

    def __init__(self, app_configs, configs, logger):
        self.commands = {}
        self.bcc = Broadcast(loop=loop)
        self.logger = logger
        self.app = GraiaMiraiApplication(
            broadcast=self.bcc,
            connect_info=Session(**app_configs),
            logger=logger
        )
        self.prefix = configs['prefix']
        self.load_mods()

    @staticmethod
    async def processor(bot, interval: int):
        message_queue = bot.message_queue
        while True:
            if not message_queue.empty():
                message = await message_queue.get()
                if type(message[0]) == list:
                    msg = message[0]
                else:
                    msg = await message[0](*message[1],**message[2])
                message_queue.task_done()
                try:
                    await bot.sendMessage(message[2]["subject"], msg)
                except KeyboardInterrupt:
                    pass
                except Exception as e:
                    bot.logger.exception(e)
            await asyncio.sleep(interval)

    def init_processors(self, num: int = 5):
        loop = asyncio.get_event_loop()
        for i in range(1, num + 1):
            loop.create_task(Bot.processor(self, i))

    def load_mods(self):
        mod_dir = Path(__file__).parent.parent.joinpath("mods")
        module_prefix = mod_dir.name

        self.commands[self.prefix + "help"] = partial(help_handler,self)
        self.commands[self.prefix + "task"] = partial(schedule_handler,self)
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
                        self.logger.error(f'未能导入 "{module_path}", error: 已存在指令{comm}')
                    else:
                        self.commands[comm], self.docs[comm] = func, func.__doc__
            self.logger.info(f'成功导入 "{module_path}"')
        except Exception as e:
            self.logger.error(f'未能导入 "{module_path}", error: {e}')
            self.logger.exception(e)

    async def sendMessage(self, subject, msg):
        if isinstance(subject, Member):
            await self.app.sendGroupMessage(subject.group, msg)
        else:
            await self.app.sendFriendMessage(subject, msg)
        pass

    async def judge(self, subject: T.Union[Member, Friend], message: MessageChain):
            try:
                message_str = message.asDisplay()
                pattern = self.prefix + r"([\S]+ )*[\S]+"
                match = re.match(pattern,message_str,re.I)
                command_str = ""
                if match:
                    command_str = message_str[match.span()[0]:match.span()[1]].lower()
                    [comm,*args] = command_str.split(" ")
                    if comm in self.commands.keys():
                        if isinstance(subject, Member):
                            self.logger.info(f"[{comm[len(self.prefix):]}]来自群{subject.group.id}中成员{subject.id}的指令:" + message_str)
                        else:
                            self.logger.info(f"[{comm[len(self.prefix):]}]来自好友{subject.id}的指令:" + message_str)
                        await self.message_queue.put((self.commands[comm], args, {"subject":subject}))
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
