import sys, subprocess, os, shutil
from playwright.sync_api import sync_playwright
S="/tmp/claude-0/-home-claude/80e7857f-008c-5260-b5ef-714e7d23e49b/scratchpad"
fmt, out = sys.argv[1], sys.argv[2]
W,H=(1080,1920) if fmt=="v" else (1080,1080)
d=f"{S}/out/rec3_{fmt}"; shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
FPS=30; N=9*FPS
with sync_playwright() as p:
  b=p.chromium.launch(); pg=b.new_page(viewport={"width":W,"height":H})
  pg.goto(f"file://{S}/brandout/anim3.html?grabar=1&f={fmt}"); pg.evaluate("document.fonts.ready"); pg.evaluate("listo()"); pg.wait_for_timeout(300)
  for i in range(N):
    pg.evaluate(f"ponerTiempo({i*1000/FPS})"); pg.screenshot(path=f"{d}/f{i:04d}.jpg", quality=95, type="jpeg")
  b.close()
subprocess.run(["ffmpeg","-y","-loglevel","error","-framerate",str(FPS),"-i",f"{d}/f%04d.jpg","-c:v","libx264","-pix_fmt","yuv420p","-crf","19","-movflags","+faststart",out],check=True)
print("ok", out)
