import json
import os
from typing import Union


def readJSON(path,
             shouldCreateFileIfNotExisted=True,
             defaultValue={}) -> Union[dict, list]:
    if not os.path.exists(path):
        if not shouldCreateFileIfNotExisted:
            return {}
        updateJSON(path, defaultValue)
    with open(path, encoding='utf-8') as f:
        d = json.loads(f.read())
    return d


def updateJSON(path, d):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(d))
