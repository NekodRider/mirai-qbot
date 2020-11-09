from os import replace
from pathlib import Path
from typing import Union, Any
from graia.application.friend import Friend
from graia.application.group import Group, Member
from collections.abc import Sequence, Mapping
import pickle


class Storage(object):
    groups = {}
    friends = {}
    path = ""

    def __init__(self):
        self.groups = {}
        self.friends = {}

    @staticmethod
    def update(d1, d2, replace, duplicate):
        for k, v in d2.items():
            if isinstance(v, Mapping):
                d1[k] = Storage.update(d1.get(k, {}), v, replace, duplicate)
            elif isinstance(v, list):
                if replace:
                    d1[k] = v
                else:
                    d1[k] = d1[k] + v if k in d1.keys() else v
                    if not duplicate:
                        d1[k] = list(set(d1[k]))
            else:
                d1[k] = v
        return d1

    def get(self,
            subject: Union[Friend, Group, Member],
            name: str,
            default: Any = {}) -> Any:
        if isinstance(subject, Friend):
            return self.friends.get(subject.id, {}).get(name) or default
        elif isinstance(subject, Group):
            return self.groups.get(subject.id, {}).get(name) or default
        elif isinstance(subject, Member):
            return self.groups.get(subject.group.id, {}).get(
                subject.id, {}).get(name) or default
        raise TypeError(type(subject))

    def set(self,
            subject: Union[Friend, Group, Member],
            kv: dict,
            replace: bool = False,
            duplicate: bool = False) -> bool:
        '''用于小范围更新值(适用于Sequence或k-v中的非Mapping的value)
        duplicate参数表示数组合并时是否允许重复
        replace参数表示数组是替换还是合并'''
        if isinstance(subject, Friend):
            tmp = {subject.id: kv}
            self.update(self.friends, tmp, replace, duplicate)
        elif isinstance(subject, Group):
            tmp = {subject.id: kv}
            self.update(self.groups, tmp, replace, duplicate)
        elif isinstance(subject, Member):
            tmp = {subject.group.id: {subject.id: kv}}
            self.update(self.groups, tmp, replace, duplicate)
        else:
            raise TypeError(type(subject))
        self.persist()
        return True

    def replace(self, subject: Union[Friend, Group, Member], kv: dict) -> bool:
        '''用于大范围替换值 比如需要替换整个dict的情况
        '''
        if isinstance(subject, Friend):
            self.friends[subject.id] = kv
        elif isinstance(subject, Group):
            self.groups[subject.id] = kv
        elif isinstance(subject, Member):
            self.groups[subject.group.id][subject.id] = kv
        else:
            raise TypeError(type(subject))
        self.persist()
        return True

    def persist(self):
        pickle.dump(
            self,
            open(
                Path(__file__).parent.parent.joinpath("data").joinpath("db"),
                'wb'))

    @staticmethod
    def load():
        path = Path(__file__).parent.parent.joinpath("data").joinpath("db")
        if path.exists():
            ret = pickle.load(open(path, 'rb'))
            return ret or Storage()
        return Storage()

    def __exit__(self):
        self.persist()
