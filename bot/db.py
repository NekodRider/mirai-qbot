from pathlib import Path
from typing import Union, Any
from graia.application.friend import Friend
from graia.application.group import Group, Member
import collections
import pickle


class Storage(object):
    groups = {}
    friends = {}
    path = ""

    def __init__(self):
        self.groups = {}
        self.friends = {}

    @staticmethod
    def update(d1, d2):
        for k, v in d2.items():
            if isinstance(v, collections.Mapping):
                d1[k] = Storage.update(d1.get(k, {}), v)
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

    def set(self, subject: Union[Friend, Group, Member], kv: dict) -> bool:
        if isinstance(subject, Friend):
            tmp = {subject.id: kv}
            self.update(self.friends, tmp)
        elif isinstance(subject, Group):
            tmp = {subject.id: kv}
            self.update(self.groups, tmp)
        elif isinstance(subject, Member):
            tmp = {subject.group.id: {subject.id: kv}}
            self.update(self.groups, tmp)
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
