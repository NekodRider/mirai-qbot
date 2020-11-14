#type: ignore
import os
import importlib
from bot import Bot

if __name__ == "__main__":
    if os.path.exists("config.py"):
        config = importlib.import_module("config")
        if all([hasattr(config, x) for x in ("app_configs", "bot_configs")]):
            bot = Bot(config.app_configs, config.bot_configs)
            bot.activate()
        else:
            print("请根据config-example.py补充config.py!")
            exit(1)
    else:
        print("请根据config-example.py创建config.py!")
        exit(1)
