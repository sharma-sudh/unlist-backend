import asyncio
from playwright.async_api import async_playwright

URL = "https://www.spinny.com/buy-used-cars/jaipur/hyundai/elite-i20/sportz-plus-12-ajmer-road-2019/29483061/?referrer=/used-cars-in-jaipur/s/"

async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # headless=False so you can see what's happening
        page = await browser.new_page()

        print("Opening listing...")
        await page.goto(URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)  # wait 3s for JS to render

        # grab all visible text on the page
        text = await page.inner_text("body")
        print("\n--- RAW PAGE TEXT ---\n")
        print(text[:5000])  # print first 5000 chars so we don't flood terminal

        await browser.close()

asyncio.run(scrape())