
def parseMsg(msg: str):
    if not msg.startswith('/'):
        return [None]
    cmd = list(filter(lambda v: v != '', map(
        lambda a: a.strip(), msg.split(' '))))
    return [cmd[0][1:].lower()] + cmd[1:]

# parseMsg('/jrrp yd td  yd   td  ')
