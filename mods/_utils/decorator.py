from ..users import getUserInfo
import time
import hashlib
import functools
import asyncio

def args_parser(num, index=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args,sender,event_type):
            if len(args) < num:
                r = getUserInfo(sender.id)
                userId = r and r['nickname']
                if userId is not None:
                    if index is not None:
                        a = list(args)
                        a.insert(index, userId)
                        args = tuple(a)
                    else:
                        args += (userId, )
            return func(*args,sender = sender,event_type = event_type)
        return wrapper
    return decorator

def make_key(args, kwds):
    m = hashlib.md5()
    for no, value in enumerate(args):
        m.update((str(no)+str(value)).encode("utf-8"))
    for k, v in kwds.items():
        m.update((str(k)+str(v)).encode("utf-8"))
    return m.hexdigest()

def api_cache(timeout = 300):
    def decorator(func):
        sentinel = object()
        cache = {}
        @functools.wraps(func)
        async def wrapper(*args, **kwds):
            key = make_key(args, kwds)
            result_time = cache.get(key, sentinel)
            if result_time is not sentinel and time.time() - result_time[1] < timeout:
                return result_time[0]
            result = await func(*args, **kwds)
            cache[key] = (result, time.time())
            return result
        return wrapper
    return decorator
