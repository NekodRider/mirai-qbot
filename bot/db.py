from pathlib import Path
from typing import Union, Any
from graia.application.friend import Friend
from graia.application.group import Group, Member
import pickle


class Storage(object):
    groups = {}
    friends = {}
    path = ""

    def __init__(self):
        self.groups = {}
        self.friends = {}

    def get(self, subject: Union[Friend, Group, Member], name: str) -> Any:
        if isinstance(subject, Friend):
            return self.friends.get(subject.id, {}).get(name)
        elif isinstance(subject, Group):
            return self.groups.get(subject.id, {}).get(name)
        elif isinstance(subject, Member):
            return self.groups.get(subject.group.id, {}).get(subject.id,
                                                             {}).get(name)
        raise TypeError(type(subject))

    def set(self, subject: Union[Friend, Group, Member], kv: dict) -> bool:
        if isinstance(subject, Friend):
            tmp = {subject.id: kv}
            self.friends.update(tmp)
        elif isinstance(subject, Group):
            tmp = {subject.id: kv}
            self.groups.update(tmp)
        elif isinstance(subject, Member):
            tmp = {subject.group.id: {subject.id: kv}}
            self.groups.update(tmp)
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
