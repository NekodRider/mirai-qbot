#encoding=Utf-8
from mirai import Mirai, Group, GroupMessage, MessageChain, Member, Plain, Image, Face, AtAll, At,FlashImage, exceptions
from mirai.logger import Session as SessionLogger
from .dance_top import getTop3DanceToday
from urllib.request import urlretrieve
from pathlib import Path

sub_app = Mirai(f"mirai://localhost:8080/?authKey=0&qq=0")

@sub_app.receiver("GroupMessage")
async def repeat_handler(app: Mirai, group:Group, message:MessageChain, member:Member):
    sender=member.id
    groupId=group.id
    if message.toString()[:6] == "/dance":
        SessionLogger.info("[DANCE]来自群%d中成员%d的消息:" % (groupId,sender) + message.toString())
        title, author, pic, url = getTop3DanceToday()
        msg = [Plain(text="B站舞蹈区实时排名前3（已剔除不适内容）")]
        for i, ti in enumerate(title):
            msg.append(Plain(text=str(i + 1) + "：" + ti + " by " + author[i]))
            msg.append(Plain(text=url[i]))
            img_path = str(Path(__file__).parent.joinpath('dance_' + str(i) + ".jpg"))
            urlretrieve(pic[i], img_path)
            msg.append(Image.fromFileSystem(img_path))
        SessionLogger.info("[DANCE]返回成功")
        try:
            await app.sendGroupMessage(group,msg)
        except exceptions.BotMutedError:
            pass

# if __name__ == "__main__":
#     title, author, pic, url = getTop3DanceToday()
#     img_path = str(Path(__file__).parent.joinpath('dance_' + str(0) + ".jpg"))
#     urlretrieve(pic[0], img_path)