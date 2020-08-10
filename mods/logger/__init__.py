from mirai import Mirai, Group, FriendMessage, GroupMessage, MessageChain, Member, Plain, Image, Face, AtAll, At,FlashImage, exceptions
from mirai.logger import Session as SessionLogger
from pathlib import Path

sub_app = Mirai(f"mirai://localhost:8080/?authKey=0&qq=0")

@sub_app.receiver(FriendMessage)
@sub_app.receiver(GroupMessage)
async def logger_handler(app: Mirai, sender: "Sender", event_type: "Type", message: MessageChain):
    if message.toString() == "/log":
        SessionLogger.info("[LOGGER]来自群%d中成员%d的消息:" % (sender.group.id,sender.id) + message.toString())
        with open(Path(__file__).parent.parent.parent.joinpath("mirai-qbot.log"),"r") as f:
            res = f.readlines()
            res = "".join(res[0 if len(res)<20 else len(res)-20:])
        try:
            msg = [Plain(text=res)]
            if event_type == "GroupMessage":
                await app.sendGroupMessage(sender.group, msg)
            elif event_type == "FriendMessage":
                await app.sendFriendMessage(sender, msg)
        except:
            pass
