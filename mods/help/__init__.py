from mirai import Mirai, Group, GroupMessage, MessageChain, Member, Plain, Image, Face, AtAll, At,FlashImage, exceptions

sub_app = Mirai(f"mirai://localhost:8080/?authKey=0&qq=0")

@sub_app.receiver(GroupMessage)
async def help_handler(app: Mirai, group:Group, message:MessageChain, member:Member):
    pass