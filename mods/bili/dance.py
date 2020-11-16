from urllib import request
from pathlib import Path
import json
import random
import os

from .api import dance_api, dance_recommend_api, video_api, block_words, up_list, block_up_list
from bot.logger import defaultLogger as logger


def checkTitle(title):
    return not any([x in title for x in block_words])


def detectSafeSearchUri(uri):
    """Detects unsafe features in the file located in Google Cloud Storage or
    on the Web."""
    config_path = Path(__file__).parent.joinpath("google_api.json")
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
    except Exception as e:
        logger.exception(e)
        return 6
    if response.error.message:
        logger.error(f"GOOGLE API ERROR: {response.error.message}")
        return 6
    safe = response.safe_search_annotation
    return safe.racy


def getRecommendDance():
    author = []
    title = []
    pic = []
    url = []
    racy = []
    for _ in range(0, 3):
        cur_url = dance_recommend_api.format(random.choice(up_list))
        try:
            html = request.urlopen(cur_url)
        except Exception as e:
            logger.exception(e)
            raise
        data = json.loads(html.read().decode('utf-8'))
        dance_list = data["data"]["list"]["vlist"]
        rand_dance = random.choice(dance_list)

        cover_url = "http:" + rand_dance["pic"]
        this_racy = detectSafeSearchUri(cover_url)
        bvid = rand_dance["bvid"]
        url.append(video_api + bvid)
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
        u_id = data["mid"]
        if checkTitle(data["title"]) == -1 or str(u_id) in block_up_list:
            continue
        count += 1
        cover_url = data["pic"]
        this_racy = detectSafeSearchUri(cover_url)
        bvid = data["bvid"]
        url.append(video_api + bvid)
        author.append(data["author"])
        title.append(data["title"])
        pic.append(cover_url)
        racy.append(this_racy)
        if count >= 3:
            break
    return title, author, pic, url, racy
