from mirai import Group,Permission

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