from ..users import getUserInfo
import time
import hashlib
import functools
import asyncio
import copy
from datetime import datetime
from .. import message_queue

schedule_task_list = []

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
            cache[key] = (copy.deepcopy(result), time.time())
            return result
        return wrapper
    return decorator

def schedule_task(name=None, interval=None, specific_time=None):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            specific_time_first = True
            global schedule_task_list
            tmp = {"name":name,"func_name":func.__name__,"interval":interval,"specific_time":specific_time}
            schedule_task_list.append(tmp)
            index = schedule_task_list.index(tmp)
            while 1:
                if interval:
                    schedule_task_list[index]["next_scheduled"] = time.time() + interval
                    await asyncio.sleep(interval)
                elif specific_time:
                    if specific_time_first:
                        h,m,s = [int(specific_time[2*i:2*i+2]) for i in range(3)]
                        next_call = datetime.now().replace(hour=h,minute=m,second=s) + datetime.timedelta(day=1)
                        remain = datetime.timestamp(next_call) - time.time()
                        schedule_task_list[index]["next_scheduled"] = datetime.timestamp(next_call)
                        await asyncio.sleep(remain)
                    else:
                        schedule_task_list[index]["next_scheduled"] = time.time() + 24*60*60
                        await asyncio.sleep(24*60*60)
                else:
                    schedule_task_list.remove(tmp)
                    raise ValueError("at least need one of interval or specific_time!")
                await func(*args, **kwargs)
                schedule_task_list[index]["last_scheduled"] = time.time()
        return wrapper
    return decorator
