from mirai import Group, Permission, Image, Face, At, AtAll, FlashImage, Plain
import re

face_list = ["jingya", "piezui", "se", "fadai", "deyi", "liulei", "haixiu", "bizui", "shui", "daku", "ganga", "fanu", "tiaopi", "ciya", "weixiao", "nanguo", "ku", "zhuakuang", "tu", "touxiao", "keai", "baiyan", "aoman", "ji_e", "kun", "jingkong", "liuhan", "hanxiao", "dabing", "fendou", "zhouma", "yiwen", "yun", "zhemo", "shuai", "kulou", "qiaoda", "zaijian", "fadou", "aiqing", "tiaotiao", "zhutou", "yongbao", "dan_gao", "shandian", "zhadan", "dao", "zuqiu", "bianbian", "kafei", "fan", "meigui", "diaoxie", "aixin", "xinsui", "liwu", "taiyang", "yueliang", "qiang", "ruo", "woshou", "shengli", "feiwen", "naohuo", "xigua", "lenghan", "cahan", "koubi", "guzhang", "qiudale", "huaixiao", "zuohengheng", "youhengheng", "haqian", "bishi", "weiqu", "kuaikule", "yinxian", "qinqin", "xia", "kelian", "caidao", "pijiu", "lanqiu", "pingpang", "shiai", "piaochong", "baoquan", "gouyin", "quantou", "chajin", "aini", "bu", "hao", "zhuanquan", "ketou", "huitou", "tiaosheng", "huishou", "jidong", "jiewu",
             "xianwen", "zuotaiji", "youtaiji", "shuangxi", "bianpao", "denglong", "facai", "K_ge", "gouwu", "youjian", "shuai_qi", "hecai", "qidao", "baojin", "bangbangtang", "he_nai", "xiamian", "xiangjiao", "feiji", "kaiche", "gaotiezuochetou", "chexiang", "gaotieyouchetou", "duoyun", "xiayu", "chaopiao", "xiongmao", "dengpao", "fengche", "naozhong", "dasan", "caiqiu", "zuanjie", "shafa", "zhijin", "yao", "shouqiang", "qingwa", "hexie", "yangtuo", "youling", "dan", "juhua", "hongbao", "daxiao", "bukaixin", "lengmo", "e", "haobang", "baituo", "dianzan", "wuliao", "tuolian", "chi", "songhua", "haipa", "huachi", "xiaoyanger", "biaolei", "wobukan", "bobo", "hulian", "paitou", "cheyiche", "tianyitian", "cengyiceng", "zhuaizhatian", "dingguagua", "baobao", "baoji", "kaiqiang", "liaoyiliao", "paizhuo", "paishou", "gongxi", "ganbei", "chaofeng", "heng", "foxi", "qiaoyiqioa", "jingdai", "chandou", "kentou", "toukan", "shanlian", "yuanliang", "penlian", "shengrikuaile", "touzhuangji", "shuaitou", "rengou"]


def groupToStr(g):
    return f"{g.id}|{g.name}|{g.permission}"

def groupFromStr(s):
    sl = s.split("|")
    if sl[2] == "Permission.Member":
        p = Permission.Member
    elif sl[2] == "Permission.Owner":
        p = Permission.Owner
    else:
        p = Permission.Administrator
    return Group(id=int(sl[0]), name=sl[1], permission=p)


def stringToMsg(s):
    comps = s.replace("[", "]").split("]")
    while '' in comps:
        comps.remove('')
    msg = []
    for i in comps:
        if "Image" in i:
            msg.append(Image(imageId=i.split("::")[-1]))
        # 需要修改Face toString方法
        elif "Face" in i:
            try:
                msg.append(Face(faceId=face_list.index(i.split("name=")[-1])))
            except ValueError:
                continue
        elif "AtAll" in i:
            msg.append(AtAll())
        elif "At" in i:
            msg.append(At(target=i.split("target=")[-1]))
        elif "FlashImage" in i:
            msg.append(FlashImage(imageId=i.split("::")[-1]))
        else:
            msg.append(Plain(text=i))
    return msg

# import re
def parseMsg(msg: str):
    if not msg.startswith('/'):
        return [None]
    arguments = list(filter(lambda v: v != '', map(
        lambda a: a.strip(), msg.split(' '))))
    cmd = arguments[0][1:].lower()
    # print(cmd)
    if not re.match('^[a-z]*$', cmd):
        # TODO: 如果有非英文命令再想办法处理一下吧
        return [None]
    return [cmd] + arguments[1:]

# parseMsg('/jrrp yd td  yd   td  ')
# parseMsg('/卧槽 yd td  yd   td  ')
