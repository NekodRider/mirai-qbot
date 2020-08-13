from mirai import Group,Permission,Image,Face,At,AtAll,FlashImage,Plain

def groupToStr(g):
    return f"{g.id}|{g.name}|{g.permission}"

def groupFromStr(s):
    sl = s.split("|")
    if sl[2]=="Permission.Member":
        p = Permission.Member
    elif sl[2]=="Permission.Owner":
        p = Permission.Owner
    else:
        p = Permission.Administrator
    return Group(id=int(sl[0]),name=sl[1],permission=p)

def stringToMsg(s):
    comps = s.replace("[","]").split("]")
    while '' in comps:
        comps.remove('')
    msg = []
    for i in comps:
        if "Image" in i:
            msg.append(Image(imageId=i.split("::")[-1]))
        #需要修改Face toString方法
        elif "Face" in i:
            msg.append(Face(faceId=i.split("faceId=")[-1]))
        elif "AtAll" in i:
            msg.append(AtAll())
        elif "At" in i:
            msg.append(At(target=i.split("target=")[-1]))
        elif "FlashImage" in i:
            msg.append(FlashImage(imageId=i.split("::")[-1]))
        else:
            msg.append(Plain(text=i))
    return msg
