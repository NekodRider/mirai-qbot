from mirai import Group, Permission, Image, Face, At, AtAll, FlashImage, Plain
from mirai.face import QQFaces
import re


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
        elif "Face" in i:
            try:
                msg.append(Face(faceId=QQFaces[i.split("name=")[-1]]))
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
