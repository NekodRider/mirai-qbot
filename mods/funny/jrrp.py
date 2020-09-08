import time
import random


def calcJrrp(groupId: int, qq: int, offset: int = 0) -> int:
    """
    0-100
    因为同 offset 同日期要产生同样的值，且不能在日期加大的时候重复，所以就这么瞎拼一下了
    """
    seed = groupId + qq + int(str(offset)+time.strftime("%Y%m%d", time.localtime()))
    random.seed(seed)
    return random.randint(0, 100)
