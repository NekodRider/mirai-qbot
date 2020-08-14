import sys
import os
from logbook import RotatingFileHandler, INFO, Logger
from mirai import Mirai
from mods import load_mods
import importlib

if __name__ == '__main__':
    if not os.path.exists('config.py'):
        print("请根据config-example.py创建config.py！")
        exit(1)
    config = importlib.import_module("config")
    app = Mirai(
        f"mirai://{config.API_URL}?authKey={config.AUTHKEY}&qq={config.BOTQQ}")

    handler = RotatingFileHandler('mirai-qbot.log', level=INFO, bubble=True,
                                  max_size=10240, backup_count=1)
    handler.format_string = '[{record.time:%Y-%m-%d %H:%M:%S}][Mirai] {record.level_name}: {record.channel}: {record.message}'
    handler.push_application()
    exceptions_logger = Logger('Exceptions')
    load_mods(app,config.PREFIX)
    try:
        app.run()
    except Exception as e:
        exceptions_logger.exception(e)