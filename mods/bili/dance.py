from logging import log
from urllib import request
from pathlib import Path
from bot.logger import defaultLogger as logger
import json
import random
import os

black_lists = ["男"]
up_lists = [
    "15385187", "84465926", "632887", "2689967", "5276", "8366990", "7375428",
    "466272", "13346799", "8581342", "475250", "13346799"
]

black_ups = ["399752044", "10139490", "643928765", "348470", "32782335"]

dance_api = "http://api.bilibili.com/x/web-interface/ranking?rid=129&day=1"
video_pri = "https://www.bilibili.com/video/"


def checkTitle(title):
    for word in black_lists:
        if word in title:
            return -1
    return 0


def detectSafeSearchUri(uri):
    """Detects unsafe features in the file located in Google Cloud Storage or
    on the Web."""
    config_path = Path(__file__).parent.joinpath(
        "Dota-Project-c6dd8c4677d4.json")
    if not config_path.exists():
        logger.info("GOOGLE API CREDENTIALS NOT FOUND!")
        return 6
    config_file = str(config_path)
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config_file

    from google.cloud import vision
    from google.api_core.exceptions import ServiceUnavailable
    client = vision.ImageAnnotatorClient()
    image = vision.types.Image()  #type: ignore
    image.source.image_uri = uri

    try:
        response = client.safe_search_detection(image=image)  #type: ignore
    except KeyboardInterrupt or SystemExit:
        return
    except Exception as e:
        logger.exception(e)
        return 6
    if response.error.message:
        logger.error(f"GOOGLE API ERROR: {response.error.message}")
        return 6
    safe = response.safe_search_annotation

    # # Names of likelihood from google.cloud.vision.enums
    # likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE',
    #                    'LIKELY', 'VERY_LIKELY')

    return safe.racy


def getRecommendDance():
    author = []
    title = []
    pic = []
    url = []
    racy = []
    for _ in range(0, 3):
        rand_user = up_lists[random.randint(0, len(up_lists) - 1)]
        cur_url = "http://api.bilibili.com/x/space/arc/search?mid=" + rand_user + "&pn=1&ps=10&tid=129"
        try:
            html = request.urlopen(cur_url)
        except KeyboardInterrupt or SystemExit:
            exit()
        except Exception as e:
            logger.exception(e)
            exit()
        data = json.loads(html.read().decode('utf-8'))
        dance_list = data["data"]["list"]["vlist"]
        rand_dance = dance_list[random.randint(0, len(dance_list) - 1)]

        cover_url = "http:" + rand_dance["pic"]
        this_racy = detectSafeSearchUri(cover_url)
        bvid = rand_dance["bvid"]
        url.append(video_pri + bvid)
        author.append(rand_dance["author"])
        title.append(rand_dance["title"])
        pic.append(cover_url)
        racy.append(this_racy)
    return title, author, pic, url, racy


def getTop3DanceToday():
    try:
        html = request.urlopen(dance_api)
    except KeyboardInterrupt or SystemExit:
        exit()
    except Exception as e:
        logger.exception(e)
        exit()
    count = 0
    dance_data = json.loads(html.read().decode('utf-8'))
    author = []
    title = []
    pic = []
    url = []
    racy = []
    for _, data in enumerate(dance_data["data"]["list"]):
        if checkTitle(data["title"]) == -1:
            continue
        u_id = data["mid"]
        if str(u_id) in black_ups:
            continue
        count += 1
        cover_url = data["pic"]
        this_racy = detectSafeSearchUri(cover_url)
        bvid = data["bvid"]
        url.append(video_pri + bvid)
        author.append(data["author"])
        title.append(data["title"])
        pic.append(cover_url)
        racy.append(this_racy)
        if count >= 3:
            break
    return title, author, pic, url, racy
