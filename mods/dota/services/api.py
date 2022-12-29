import requests
import json

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

from ..constants.heros import HERO_EN_DICT,HERO_CN_DICT
from _utils.rate_limiter import RateLimiter

CUSTOM_HEADER = {"User-Agent": "Chrome/69.0.3497.81 Safari/537.36"}


class API():

    def test(self):
        return all([requests.get(url).status_code == 200 for url in self.testURLs])

    @RateLimiter(30)
    def getRawJson(url):
        req = requests.Request(url)
        req.add_header(CUSTOM_HEADER)
        html = requests.get(req)
        return json.loads(html.read().decode("utf-8"))


class OfficialDotaAPI(API):
    testURLs = ["http://www.dota2.com/datafeed/"]

    def patch_list():
        return 'http://www.dota2.com/datafeed/patchnoteslist'

    def patch_notes(version):
        return f'http://www.dota2.com/datafeed/patchnotes?version={version}&language=english'

    def item():
        return 'http://www.dota2.com/datafeed/itemlist?language=schinese'

    def ability():
        return 'http://www.dota2.com/datafeed/abilitylist?language=schinese'

    def hero():
        return 'http://www.dota2.com/datafeed/herolist?language=schinese'


class StratzAPI(API):
    testURLs = ["https://api.stratz.com/api/v1/"]
    
    def __init__(self,gql_key=None):
        self._gql_key = gql_key

    def player_match_info(self, player_id, params):
        return f"https://api.stratz.com/api/v1/player/{player_id}/matches{params}"

    def player_hero_performance(self, player_id, hero_id):
        return f"https://api.stratz.com/api/v1/Player/{player_id}/heroPerformance/{hero_id}?gameMode=1,2,3,4",

    def gql_root(self):
        return f"https://api.stratz.com/graphql?key={self._gqlkey}"

    def match_detail_gql(player_id, match_id):
        return """
            query{{
                player(steamAccountId:{}){{
                    matches(request:{{{}gameModeIds:[1,2,3,4]}}){{
                        startDateTime,
                        durationSeconds,
                        players{{
                            steamAccount{{
                                name,
                                id
                            }}
                            isVictory,
                            imp,
                            role,
                            lane,
                            heroId,
                            kills,
                            deaths,
                            assists,
                            numLastHits,
                            numDenies,
                            goldPerMinute,
                            heroDamage,
                            towerDamage,
                            heroHealing,
                            experiencePerMinute
                        }}
                    }}
                }}
            }}
    """.format(player_id, match_id)

    def getDotaGamesInfo(self, player_id, match_args=""):
        games_data = self.getRawJson(self.player_match_info(
            player_id, match_args))
        return games_data

    async def getDotaGamesInfoGQL(self,playerId, total=0):
        result = None
        transport = AIOHTTPTransport(
            url=self.gql_root
        )
        async with Client(
                transport=transport,
                fetch_schema_from_transport=True,
        ) as session:
            q = gql(self.match_detail_gql(
                playerId, f"take:{total}," if total else ""))
            result = (await session.execute(q))["player"]["matches"]
        return result


class OpendotaAPI(API):
    testURLs = ["https://api.opendota.com/api/"]

    def player(self, player_id, params):
        return f"https://api.opendota.com/api/players/{player_id}{params}"

    def player_recent_matches(self, player_id, params):
        return f"https://api.opendota.com/api/players/{player_id}/recentMatches"

    def player_hero_performance(self, player_id, hero_id):
        return f"https://api.opendota.com/api/players/{player_id}/heroes/?hero_id={hero_id}"

    def match(match_id):
        return f"https://api.opendota.com/api/matches/{match_id}"

    def match_story(match_id):
        return f'https://www.opendota.com/matches/{match_id}/story'

    def match_request(match_id):
        return f'https://www.opendota.com/request#{match_id}'

    def getPlayerInfo(self, playerId, playerArgs="") -> dict:
        player_data = self.getRawJson(self.player(playerId, playerArgs))
        return player_data

    def getRecentMatches(self, player_id):
        games_data = self.getRawJson(
            self.player_recent_matches(player_id))
        return games_data

    def getNameDict(self, match_id):
        players_data = self.getRawJson(self.match(match_id))["players"]
        res = {}
        for p in players_data:
            if "personaname" in p.keys():
                res[HERO_EN_DICT[str(p["hero_id"])]] = p["personaname"]
        return res

    def getDotaHero(self,playerId, heroName):
        res = {}
        hero_id = -1
        for k, v in HERO_CN_DICT.items():
            if v == heroName:
                res["hero"] = v
                hero_id = k
                break
        player_info = self.getPlayerInfo(playerId)
        if hero_id == -1 or not player_info:
            return None
        res["name"] = player_info["profile"]["personaname"]
        data = self.getRawJson(self.player_hero_performance(playerId, hero_id))
        if not data:
            return f"{res['name']} 也配玩 {res['hero']}?"
        res["win_stat"] = f"{round(data['winCount']/data['matchCount']*100,2)}% - {data['winCount']}W/{data['matchCount']-data['winCount']}L"
        res["kda"] = f"{int(data['avgNumKills'])}/{int(data['avgNumDeaths'])}/{int(data['avgNumAssists'])}"
        res["gpm"] = int(data["avgGoldPerMinute"])

        def getLaneMatchCount(elem):
            return elem["laneMatchCount"]

        def getRoleLaneMatchCount(elem):
            return elem["lanes"][0]["laneMatchCount"]

        for role in data["position"]:
            role["lanes"].sort(key=getLaneMatchCount, reverse=True)

        data["position"].sort(key=getRoleLaneMatchCount, reverse=True)
        role = data["position"][0]

        res["role"] = f"在{round(role['lanes'][0]['laneMatchCount']/data['matchCount']*100,2)}%的比赛中担任"
        res["role"] += ("优势路" if role["lanes"][0]["laneType"] == 1 else
                        ("中路" if role["lanes"][0]["laneType"] == 2 else
                        ("游走" if role["lanes"][0]["laneType"] == 0 else "劣势路")))
        res["role"] += "核心" if role["roleType"] == 0 else "辅助"
        result = f"{res['name']} 使用 {res['hero']} {res['role']}\n胜率: {res['win_stat']}  KDA: {res['kda']}  GPM: {res['gpm']}"
        return result
