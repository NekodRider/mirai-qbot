import sys
import os
from logbook import RotatingFileHandler, INFO
from mirai import Mirai
from mirai.logger import Session as SessionLogger
from mods import load_mods
import importlib

if __name__ == '__main__':
    if not os.path.exists('config.py'):
        print("请根据config-example.py创建config.py！")
        exit(1)
    config = importlib.import_module("config")
    if not os.path.exists('mods/dota/dota_id.json'):
        with open('mods/dota/dota_id.json','w') as f:
            f.write("{}")
    app = Mirai(f"mirai://{config.API_URL}?authKey={config.AUTHKEY}&qq={config.BOTQQ}")
    handler = RotatingFileHandler('/var/log/mirai-qbot.log', level=INFO, bubble = True, 
                                   max_size=10240,backup_count=1)
    handler.format_string = '[{record.time:%Y-%m-%d %H:%M:%S}][Mirai] {record.level_name}: {record.channel}: {record.message}'
    handler.push_application()
    load_mods(app)
    app.run()
