# coding=utf-8
import asyncio
import matplotlib
import os
import shutil
from pathlib import Path
from pyppeteer import launch

font_file = "./resource/wqy-microhei.ttc"
sys_font_dir = "/usr/share/fonts/truetype"
# 查找字体路径
rc_file = matplotlib.matplotlib_fname()
font_path = Path(rc_file).parent.joinpath("fonts", "ttf")
shutil.copyfile(font_file, font_path.joinpath("wqy-microhei.ttc"))
shutil.copyfile(font_file, Path(sys_font_dir).joinpath("wqy-microhei.ttc"))
shutil.copy(rc_file, Path(rc_file).parent.joinpath("matplotlibrc.bak"))
flist = []
with open(rc_file, "r", encoding='utf-8') as f:
    flist = f.readlines()
    a, b = False, False
    for no, line in enumerate(flist):
        if not a and "font.family:" in line:
            a = True
            flist[no] = "font.family : sans-serif\n"
        elif not b and "font.sans-serif:" in line:
            b = True
            flist[no] = "font.sans-serif : WenQuanYi Micro Hei, Arial, Bitstream Vera Sans, Lucida Grande, Verdana, Geneva, Lucid, Helvetica, Avant Garde, sans-serif\n"
        if a and b:
            break
with open(rc_file, "w", encoding='utf-8') as f:
    f.writelines(flist)
font_cache_path = matplotlib.get_cachedir()
shutil.rmtree(font_cache_path)
os.system("timedatectl set-timezone Asia/Shanghai")
os.system("apt install fontconfig gconf-service libasound2 libatk1.0-0 libatk-bridge2.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils wget")
os.system("fc-cache -fv")

async def main():
    browser = await launch(args=['--no-sandbox'])
    page = await browser.newPage()
    await browser.close()

asyncio.run(main())
