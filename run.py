import sys
import os
from mirai import Mirai
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
    load_mods(app)
    app.run()
