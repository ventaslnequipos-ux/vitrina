"""Convierte las páginas .dc.html del catálogo en un PDF tamaño carta."""
import json, re, sys, pathlib
from PIL import Image
from playwright.sync_api import sync_playwright

S = pathlib.Path(sys.argv[1])          # scratchpad
OUT = pathlib.Path(sys.argv[2])        # pdf de salida
proj = S / "cat" / "project"
img = S / "img"
fonts = S / "fonts" / "gf" / "ofl"
work = S / "pdfwork"; work.mkdir(exist_ok=True)

BLOBS = {
 "bcae2cacebaac65e67b4963530398e87": "dieci", "e6ab7c2d2eccccd945211d291d09eaa4": "dieci_stock",
 "9e7976cbe1df3920357f9ac8e314ff34": "mg120_a", "6c9b855d0e1b815b778f2578192d7f76": "mg120_b",
 "47c8e9e6a23f40d86954b9f3b422e778": "mg140", "c1aeb4c19d2cc2bfa3b150034e592576": "cp433",
 "5ce49eb15d6f8039a085a572f92226d4": "combo", "ef21a66f9d38b82c567adc4e7baf4f52": "jcb",
 "e97e3780e442d0fad747131ca330304e": "doosan", "b3226b8406c48f70055be0841f90318c": "ford_a",
 "d9d0910a835e4eee63026c5ef9ba0e63": "ford_b", "13796dfddd09040ebcd5fb50d0d41afe": "bomag2",
 "bd551682f9266a75f41d9856b968d3ae": "duster_a", "0f7c31597460b0bf362ab404b55ec719": "duster_b",
 "8341114410326862d4b87bff5263cacc": "hitachi", "a49e3711fb99237e72f7323ef081b5a5": "ir_a",
 "795170e589f67e1beb3664808bd294df": "ir_b",
 "1ad2ee1f5db4eb034ae43f1650fd4037": "tanque", "4b4c43e6274afd579962b71f03f6f5ff": "h940",
 "78d921cc4ac6d6367137819acc1be1ef": "kia", "c60776d67ddd69ddf30b52ca91242d6b": "ss250",
 "142cdc4881bb475befdda6cdeaddb9bd": "liugong",
}
# imágenes más livianas para el PDF (WhatsApp)
for bid, name in BLOBS.items():
    dst = work / f"{name}.jpg"
    if not dst.exists():
        im = Image.open(img / f"{name}.jpg"); im.thumbnail((1100, 1100))
        im.save(dst, quality=74, optimize=True, progressive=True)

order = json.loads((proj / "canvas.json").read_text())["order"]
pages = []
for f in order:
    src = (proj / f).read_text()
    body = src.split("<x-dc>", 1)[1].split("</x-dc>", 1)[0]
    body = re.sub(r"<helmet>.*?</helmet>", "", body, flags=re.S)
    body = re.sub(r"/_blob/([0-9a-f]{32})", lambda m: f"{BLOBS[m.group(1)]}.jpg", body)
    pages.append(f'<section class="page">{body}</section>')

ff = []
for fam, d, pre, weights in [("Barlow", "barlow", "Barlow", {400: "Regular", 500: "Medium", 600: "SemiBold"}),
                             ("Barlow Condensed", "barlowcondensed", "BarlowCondensed", {500: "Medium", 600: "SemiBold", 700: "Bold"})]:
    for w, n in weights.items():
        ff.append(f"@font-face{{font-family:'{fam}';font-weight:{w};src:url('file://{fonts}/{d}/{pre}-{n}.ttf')}}")

html = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Catálogo de venta de maquinaria</title>
<style>{''.join(ff)}
@page{{size:8.5in 11in;margin:0}} html,body{{margin:0;padding:0}}
.page{{width:816px;height:1056px;overflow:hidden;page-break-after:always;break-after:page}}
.page:last-child{{page-break-after:auto;break-after:auto}}
</style></head><body>{''.join(pages)}</body></html>"""
(work / "catalogo.html").write_text(html)

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 816, "height": 1056})
    pg.goto(f"file://{work}/catalogo.html"); pg.wait_for_load_state("networkidle")
    pg.evaluate("document.fonts.ready")
    pg.pdf(path=str(OUT), width="8.5in", height="11in", print_background=True, margin={"top":"0","bottom":"0","left":"0","right":"0"})
    b.close()
print("ok", OUT, OUT.stat().st_size, "bytes,", len(pages), "páginas")
