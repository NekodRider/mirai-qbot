
def parseMsg(msg: str):
    if not msg.startswith('/'):
        return None
    cmd = list(filter(lambda v: v != '', map(
        lambda a: a.strip(), msg.split(' '))))
    return [cmd[0].lower()] + cmd[1:]

# parseMsg('/fuCk yd td  yd   td  ')
