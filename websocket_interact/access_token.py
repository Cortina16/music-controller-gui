import asyncio
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright


# Configuration
load_dotenv()
SP_DC = os.getenv("SP_DC_COOKIE")
TARGET_URL = "https://open.spotify.com/"
TOKEN_ENDPOINT = "/api/token"


async def snipe_token():
    async with async_playwright() as p:

        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        print(SP_DC)
        await context.add_cookies([{
            'name': 'sp_dc',
            'value': SP_DC,
            'domain': '.spotify.com',
            'path': '/'
        }])

        token = None

        async def handle_response(response):
            nonlocal token
            if TOKEN_ENDPOINT in response.url:
                try:
                    json_data = await response.json()
                    if "accessToken" in json_data:
                        token = json_data["accessToken"]
                        print(f"[+] Sniped Access Token: {token[:50]}...")
                        return token
                except:
                    pass

        context.on("response", handle_response)

        page = await context.new_page()
        await page.goto(TARGET_URL)

        for _ in range(10):
            if token: break
            await asyncio.sleep(1)

        await browser.close()
        return token


if __name__ == "__main__":
    asyncio.run(snipe_token())