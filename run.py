#type: ignore
import os
import importlib

from bot import Bot

if __name__ == "__main__":
    if not os.path.exists("config.py"):
        print("请根据config-example.py创建config.py！")
        exit(1)
    config = importlib.import_module("config")
    bot = Bot(config.app_configs, config.bot_configs)
    bot.activate()
