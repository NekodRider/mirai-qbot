import asyncio
from pyppeteer import launch
from pathlib import Path
from .helper import getNameDict

async def getDotaStory(matchId):
    browser = await launch(args=['--no-sandbox'])
    page = await browser.newPage()
    await page.setViewport({"width": 800,"height": 900})
    await page.goto(f'https://www.opendota.com/matches/{matchId}/story')
    await page.evaluate("localStorage.setItem('localization', 'zh-CN');")
    await page.reload({'waitUntil' : 'networkidle0'})
    name_dict = getNameDict(matchId)
    for hero,name in name_dict.items():
        await page.evaluate(f'(()=>{{var html = document.querySelector("body").innerHTML; html = html.split("{hero}").join("{name}"); document.querySelector("body").innerHTML = html}})()',force_expr=True)

    not_found = await page.querySelector(".FourOhFour")
    unparsed = await page.querySelector(".unparsed")
    if not_found:
        await browser.close()
        return 404
    if unparsed:
        await page.goto(f'https://www.opendota.com/request#{matchId}')
        await asyncio.sleep(5)
        await browser.close()
        return 1

    body = await page.querySelector("body")
    body_bb = await body.boundingBox()
    height = body_bb['height']
    path = str(Path(__file__).parent.joinpath(f'story_{matchId}.png'))
    await page.screenshot({'path': path,'clip':{'x':0,'y':180,'width':800,'height':height-320}})
    await browser.close()
    return path