from graia.application.group import Group, MemberPerm

def groupToStr(g):
    return f"{g.id}|{g.name}|{g.accountPerm}"

def groupFromStr(s):
    sl = s.split("|")
    if sl[2] == "MEMBER":
        p = MemberPerm.Member
    elif sl[2] == "OWNER":
        p = MemberPerm.Owner
    else:
        p = MemberPerm.Administrator
    return Group(id=int(sl[0]), name=sl[1], accountPerm=p)