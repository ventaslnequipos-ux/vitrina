import sys
from playwright.sync_api import sync_playwright
S="/tmp/claude-0/-home-claude/80e7857f-008c-5260-b5ef-714e7d23e49b/scratchpad"
fmt, times, out = sys.argv[1], [int(x) for x in sys.argv[2].split(",")], sys.argv[3]
extra = sys.argv[4] if len(sys.argv)>4 else ""
W,H=(1080,1920) if fmt=="v" else (1080,1080)
with sync_playwright() as p:
  b=p.chromium.launch(); pg=b.new_page(viewport={"width":W,"height":H})
  pg.goto(f"file://{S}/brandout/anim3.html?grabar=1&f={fmt}{extra}"); pg.evaluate("document.fonts.ready"); pg.evaluate("listo()"); pg.wait_for_timeout(300)
  for i,t in enumerate(times):
    pg.evaluate(f"ponerTiempo({t})"); pg.screenshot(path=out % i)
  b.close()
