import json
import time

import requests

# from .constants import api_dict
# from .._utils.storage import updateJSON
from bot import defaultLogger as logger


def updateJSON(path, d):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(d))


api_dict = {
    "patch_list":
        'http://www.dota2.com/datafeed/patchnoteslist',
    "patch_notes":
        'http://www.dota2.com/datafeed/patchnotes?version={}&language=english',
    "item_api":
        'http://www.dota2.com/datafeed/itemlist?language=schinese',
    "ability_api":
        'http://www.dota2.com/datafeed/abilitylist?language=schinese',
    "hero_api":
        'http://www.dota2.com/datafeed/herolist?language=schinese',
}

item_dict = {}
hero_dict = {}
ability_dict = {}


def getLatestPatch():
    try:
        req = requests.get(api_dict["patch_list"])
    except Exception as e:
        logger.exception(e)
        raise
    patch_list = json.loads(req.text)
    if "patches" not in patch_list.keys():
        logger.exception("patch list api error!")
        raise
    patch_list = sorted(patch_list["patches"],
                        key=lambda x: x["patch_timestamp"])
    latest_version = patch_list[-1]
    if time.time() - latest_version["patch_timestamp"] < 180:
        res = {'title': latest_version["patch_name"]}
        try:
            req = requests.get(api_dict["patch_notes"].format(
                latest_version["patch_name"]))
        except Exception as e:
            logger.exception(e)
            raise
        patch_detail = json.loads(req.text)
        if "patch_website" in patch_detail.keys():
            res["url"] = f"http://www.dota2.com/{patch_detail['patch_website']}"
        return res
    return None


def stringfy_notes(raw: dict):
    ret = ""
    if not raw["success"]:
        return ret
    if "patch_website" in raw.keys():
        return f"http://www.dota2.com/{raw['patch_website']}"
    if "generic" in raw.keys():
        ret += "综合改动：\n"
        for line in raw["generic"]:
            ret += "  " * line["indent_level"]
            if "hide_dot" not in line.keys():
                ret += "- "
            ret += line["note"] + "\n"
            if "postfix_lines" in line.keys():
                ret += "\n"
        ret += "\n"
    if "items" in raw.keys():
        ret += "物品改动：\n"
        for line in raw["items"]:
            ret += f"  {item_dict[line['ability_id']]}:\n"
            for note in line["ability_notes"]:
                ret += "  - " + note["note"] + "\n"
            ret += "\n"
        ret += "\n"
    if "neutral_items" in raw.keys():
        ret += "中立物品改动：\n"
        for line in raw["neutral_items"]:
            ret += f"  {item_dict[line['ability_id']]}:\n"
            for note in line["ability_notes"]:
                ret += "  - " + note["note"] + "\n"
            ret += "\n"
        ret += "\n"
    if "heroes" in raw.keys():
        ret += "英雄改动：\n"
        for line in raw["heroes"]:
            ret += f"  {hero_dict[line['hero_id']]}:\n"
            if "hero_notes" in line:
                for note in line["hero_notes"]:
                    ret += "  - " + note["note"] + "\n"
            if "talent_notes" in line:
                for note in line["talent_notes"]:
                    ret += "  - " + note["note"] + "\n"
            if "abilities" in line:
                for ability in line["abilities"]:
                    ret += f"   -{ability_dict[ability['ability_id']]}:\n"
                    for note in ability["ability_notes"]:
                        ret += "    - " + note["note"] + "\n"
            ret += "\n"
        ret += "\n"
    return ret


def update_items():
    raw = json.loads(requests.get(api_dict["item_api"]).text)
    global item_dict
    item_dict = {}
    for item in raw["result"]["data"]["itemabilities"]:
        item_dict[item["id"]] = item["name_loc"] if "name_loc" in item.keys(
        ) else item["name_english_loc"]
    updateJSON("items.json", item_dict)


def update_heroes():
    raw = json.loads(requests.get(api_dict["hero_api"]).text)
    global hero_dict
    hero_dict = {}
    for hero in raw["result"]["data"]["heroes"]:
        hero_dict[hero["id"]] = hero["name_loc"] if "name_loc" in hero.keys(
        ) else hero["name_english_loc"]
    updateJSON("heroes.json", hero_dict)


def update_abilities():
    raw = json.loads(requests.get(api_dict["ability_api"]).text)
    global ability_dict
    ability_dict = {}
    for ability in raw["result"]["data"]["itemabilities"]:
        ability_dict[
            ability["id"]] = ability["name_loc"] if "name_loc" in ability.keys(
            ) else ability["name_english_loc"]
    updateJSON("abilities.json", ability_dict)


if __name__ == "__main__":
    update_items()
    update_abilities()
    update_heroes()
    raw = json.loads(requests.get(api_dict["patch_notes"].format("7.28a")).text)
    with open("res.txt", 'w', encoding='utf-8') as f:
        f.write(stringfy_notes(raw))
    print(getLatestPatch())