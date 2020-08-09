import sys
from mirai import Mirai
from mods import load_mods
from config import *

if __name__ == '__main__':
    app = Mirai(f"mirai://{API_URL}?authKey={AUTHKEY}&qq={BOTQQ}")
    load_mods(app)
    app.run()
