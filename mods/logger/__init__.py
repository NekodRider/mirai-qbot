from mirai import Mirai, Group, FriendMessage, GroupMessage, MessageChain, Member, Plain, Image, Face, AtAll, At,FlashImage, exceptions
from mirai.logger import Session as SessionLogger

sub_app = Mirai(f"mirai://localhost:8080/?authKey=0&qq=0")

@sub_app.receiver(FriendMessage)
@sub_app.receiver(GroupMessage)
async def logger_handler(app: Mirai, sender: "Sender", event_type: "Type", message: MessageChain):
    if message.toString() == "/log":
        with open("/var/log/mirai-qbot.log","r") as f:
            res = f.readlines()
            res = res[len(res)-20:]
        try:
            msg = [Plain(text=res)]
            if event_type == "GroupMessage":
                await app.sendGroupMessage(sender.group, msg)
            elif event_type == "FriendMessage":
                await app.sendFriendMessage(sender, msg)
        except:
            pass
