import json
import os

def readJSON(path, shouldCreateFileIfNotExisted=True, defaultValue={}):
    if not os.path.exists(path):
        if not shouldCreateFileIfNotExisted:
            return None
        updateJSON(path, defaultValue)
    with open(path, encoding='utf-8') as f:
        d = json.loads(f.read())
    return d


def updateJSON(path, d):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(d))
