import asyncio
from pyppeteer import launch
from pathlib import Path

async def getDotaStory(matchId):
    browser = await launch()
    page = await browser.newPage()
    await page.setViewport({"width": 1400,"height": 900})
    await page.goto(f'https://www.opendota.com/matches/{matchId}/story')
    await page.waitForSelector("#root > div > div:nth-child(1) > div:nth-child(3) > button")
    await page.click("#root > div > div:nth-child(1) > div:nth-child(3) > button")
    await page.waitForSelector("body > div:last-child > div:nth-child(3) > ul > div > div")
    await page.click("body > div:last-child > div:nth-child(3) > ul > div > div")
    await page.waitForSelector("body > div:last-child > div:nth-child(3) > ul > div > div:nth-child(2) > div > div > div > div > div:last-child")
    await page.click("body > div:last-child > div:nth-child(3) > ul > div > div:nth-child(2) > div > div > div > div > div:last-child")
    await asyncio.sleep(7)

    not_found = await page.querySelector(".FourOhFour")
    if not_found:
        await browser.close()
        return 404

    body = await page.querySelector("body")
    body_bb = await body.boundingBox()
    height = body_bb['height']
    path = str(Path(__file__).parent.joinpath(f'story_{matchId}.png'))
    await page.screenshot({'path': path,'clip':{'x':0,'y':180,'width':1400,'height':height-320}})
    await browser.close()
    return path