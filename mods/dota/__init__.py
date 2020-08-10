#encoding=Utf-8
from mirai import Mirai, Group, GroupMessage, MessageChain, Member, Plain, Image, Face, AtAll, At,FlashImage, exceptions
from .helper import readDict, updateDict, getDotaPlayerInfo, getDotaGamesInfo, error_codes
from .games_24hrs import getGamesIn24Hrs
# from .winning_rate import getWinningRateGraph
from pathlib import Path

sub_app = Mirai(f"mirai://localhost:8080/?authKey=0&qq=0")
dota_id_dict = readDict()


@sub_app.receiver("GroupMessage")
async def dota_handler(app: Mirai, group:Group, message:MessageChain, member:Member):
    if message.toString()[:5] == "/dota":
        query_id = message.toString()[6:]
        if query_id in dota_id_dict.keys():
            query_id = dota_id_dict[query_id]
        res = getGamesIn24Hrs(query_id)
        msg = [Plain(text=res)]
        try:
            await app.sendGroupMessage(group,msg)
        except exceptions.BotMutedError:
            pass
    # elif message.toString()[:8] == "/winrate":
    #     query_id = message.toString()[9:].split(" ")
    #     args = 50
    #     if len(query_id) == 2:
    #         try:
    #             args = int(query_id[1])
    #             if args > 50 or args <= 0:
    #                 args = 50
    #         except ValueError:
    #             args = 50
    #     name, res = getWinningRateGraph(query_id[0], args)
    #     if type(res) == type(0):
    #         msg = [Plain(text=name)]
    #     else:
    #         img_path = Path(__file__).parent.joinpath(res)
    #         msg = [
    #             Image.fromFileSystem(str(img_path)),
    #             Plain(text=name + "最后" + str(args) + "游戏胜率变化图")
    #         ]
    #     try:
    #         await app.sendGroupMessage(group,msg)
    #     except exceptions.BotMutedError:
    #         pass
    elif message.toString()[:8] == "/setdota":
        rec = message.toString()[9:].split(" ")
        dota_id_dict[rec[0]] = rec[1]
        updateDict(dota_id_dict)
        msg = [Plain(text="添加成功！")]
        try:
            await app.sendGroupMessage(group,msg)
        except exceptions.BotMutedError:
            pass


# if __name__ == "__main__":
#     message = "/winrate 309000276 50"
#     query_id = message[9:].split(" ")
#     args = 50
#     if len(query_id) == 2:
#         try:
#             args = int(query_id[1])
#             if args > 50 or args <= 0:
#                 print("error")
#         except ValueError:
#             print("error")
#     name, res = getWinningRateGraph(query_id[0], args)
#     if type(res) == type(0):
#         print(name)
#     # img_path = Path(__file__).parent.joinpath(res)
#     # print(img_path, name)
#     # print(getWinningRateGraph("309000276"))