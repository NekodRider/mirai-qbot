import matplotlib
import os
import shutil
from pathlib import Path

font_file = "./resource/wqy-microhei.ttc"
# 查找字体路径
font_path = matplotlib.matplotlib_fname()
shutil.copyfile(font_file,os.path.join(font_path,"wqy-microhei.ttc"))
rc_file = Path(font_path).parent.parent.joinpath("mpl-data","matplotlibrc")
with open(rc_file,"a") as f:
    f.write("font.family  : sans-serif")
    f.write("font.sans-serif : WenQuanYi Micro Hei, Arial, Bitstream Vera Sans, Lucida Grande, Verdana, Geneva, Lucid, Helvetica, Avant Garde, sans-serif")
# 查找字体缓存路径
font_cache_path = matplotlib.get_cachedir()
shutil.rmtree(font_cache_path)
os.system("timedatectl set-timezone Asia/Shanghai")