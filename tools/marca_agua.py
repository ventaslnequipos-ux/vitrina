"""Pone la marca de agua Yellow Yard (placa + 'by Nestor Sierra') a las fotos del catálogo.
Fuente sin marca: scratchpad/img_limpias/*.jpg  ->  salida: scratchpad/site/img/*.jpg
Uso: python3 marca_agua.py [archivo.jpg ...]   (sin argumentos procesa todas)"""
import sys, os, glob
from PIL import Image
S="/tmp/claude-0/-home-claude/80e7857f-008c-5260-b5ef-714e7d23e49b/scratchpad"
MARCA=f"{S}/brandout/marca.png"
if not os.path.exists(MARCA):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b=p.chromium.launch(); pg=b.new_page(device_scale_factor=2); pg.goto(f"file://{S}/brandout/marca.html")
        pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
        pg.locator("#m").screenshot(path=MARCA, omit_background=True); b.close()
marca=Image.open(MARCA).convert("RGBA")
fs=sys.argv[1:] or [os.path.basename(f) for f in glob.glob(f"{S}/img_limpias/*.jpg")]
for f in fs:
    im=Image.open(f"{S}/img_limpias/{f}").convert("RGB"); w,h=im.size
    mw=max(130, int(min(w, h*1.2)*0.20)); mk=marca.resize((mw, int(marca.height*mw/marca.width)), Image.LANCZOS)
    a=mk.split()[3].point(lambda v: int(v*0.95)); mk.putalpha(a)
    m=int(min(w,h)*0.025)
    im.paste(mk,(w-mk.width-m, h-mk.height-m), mk)
    im.save(f"{S}/site/img/{f}", quality=88)
print(len(fs), "fotos con marca de agua")
