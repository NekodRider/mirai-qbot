from mirai import Mirai, GroupMessage, Group, MessageChain, Member

sub_app = Mirai(f"mirai://localhost:8080/?authKey=0&qq=0")


@sub_app.receiver("GroupMessage")
async def jrrp_handler(app: Mirai, group: Group, message: MessageChain, member: Member):
