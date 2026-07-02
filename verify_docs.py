import asyncio
from playwright.async_api import async_playwright

async def verify():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            await page.goto("http://127.0.0.1:8000")
            await page.screenshot(path="docs_index.png")
            print("Captured docs_index.png")

            await page.click("text=English Documentation")
            await page.wait_for_load_state("networkidle")
            await page.screenshot(path="docs_en.png")
            print("Captured docs_en.png")

            await page.goto("http://127.0.0.1:8000")
            await page.click("text=中文文档")
            await page.wait_for_load_state("networkidle")
            await page.screenshot(path="docs_zh.png")
            print("Captured docs_zh.png")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

asyncio.run(verify())
