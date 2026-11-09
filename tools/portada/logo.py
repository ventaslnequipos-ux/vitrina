import asyncio, sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width":200,"height":250}, device_scale_factor=2)
        svg=open("/home/claude/vitrina/logo.svg").read()
        await pg.set_content(f"<html><body style='margin:0;background:transparent'>{svg.replace('<svg ','<svg width=200 height=250 ',1)}</body></html>")
        await pg.screenshot(path=sys.argv[1], omit_background=True, clip={"x":0,"y":0,"width":200,"height":250})
        await b.close()
asyncio.run(main())
