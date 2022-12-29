# coding=utf-8
#type: ignore
import importlib
import os

import sentry_sdk

from bot import Bot

if __name__ == "__main__":
    if os.path.exists("config.py"):
        config = importlib.import_module("config")
        if all([hasattr(config, x) for x in ("app_configs", "bot_configs")]):
            # 注释下面一行来关闭 sentry
            if(config.app_configs["sentry"]):
                sentry_sdk.init(**config.app_configs["sentry_sdk"])
            bot = Bot(config.app_configs, config.bot_configs)
            bot.activate()
        else:
            print("config.py中配置缺失!")
            exit(1)
    else:
        print("请根据config-example.py创建config.py!")
        exit(1)
