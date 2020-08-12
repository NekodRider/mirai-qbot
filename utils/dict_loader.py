import json
import os


def readDict(path, createFileIfNotExisted=True, defaultValue={}):
    if not os.path.exists(path):
        if not createFileIfNotExisted:
            return None
        updateDict(path, defaultValue)
    with open(path, encoding='utf-8') as f:
        d = json.loads(f.read())
    return d


def updateDict(path, d):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(d))
