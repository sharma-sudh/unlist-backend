import asyncio
from playwright.async_api import async_playwright
import json

URL = "https://www.spinny.com/buy-used-cars/jaipur/hyundai/elite-i20/sportz-plus-12-ajmer-road-2019/29483061/?referrer=/used-cars-in-jaipur/s/"

async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()

        # load saved cookies
        with open("spinny_cookies.json", "r") as f:
            cookies = json.load(f)
        await context.add_cookies(cookies)
        print("Cookies loaded")

        page = await context.new_page()

        print("Opening listing...")
        await page.goto(URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)

        # click "View full report"
        try:
            view_report = page.get_by_text("View full report")
            await view_report.click()
            print("Clicked 'View full report'")
            await page.wait_for_timeout(3000)
        except Exception as e:
            print(f"Couldn't click 'View full report': {e}")

        text = await page.inner_text("body")
        print("\n--- RAW PAGE TEXT ---\n")
        print(text[:10000])

        await browser.close()

asyncio.run(scrape())