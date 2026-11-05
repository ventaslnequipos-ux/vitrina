#!/usr/bin/env python3
"""Crea una página corta por equipo (e/<lote>/index.html) en la rama main.

Sirve para que, al compartir o consultar por WhatsApp, el enlace del equipo muestre
la FOTO DE ESE EQUIPO con su nombre y precio en la vista previa. La página lleva al
visitante enseguida a la ficha del equipo en el catálogo (…/#lote-XX).

Uso: python3 fichas_compartir.py <carpeta de la rama main>
publicar.py la llama sola después de generar equipos.js.
"""
import html, json, os, shutil, subprocess, sys

SITIO = "https://ventaslnequipos-ux.github.io/vitrina/"

def cargar(site):
    js = os.path.join(site, "equipos.js")
    out = subprocess.check_output(["node", "-e", """
const src = require('fs').readFileSync(process.argv[1], 'utf8');
const f = new Function(src + '; return { E: EQUIPOS, V: typeof VENDIDOS !== "undefined" ? VENDIDOS : {} };');
process.stdout.write(JSON.stringify(f()));""", js])
    return json.loads(out)

def cop(n):
    return "$" + f"{int(n):,}".replace(",", ".") if n and n > 0 else "Precio a consultar"

def main(site):
    d = cargar(site)
    base = os.path.join(site, "e")
    if os.path.isdir(base):
        shutil.rmtree(base)
    for i, e in enumerate(d["E"]):
        lote = e.get("lote") or str(i + 1).zfill(2)
        vendido = bool(d["V"].get(e["nombre"]))
        anio = str(e.get("anio") or "")
        nombre = e["nombre"] + (" " + anio if anio and anio not in e["nombre"] else "")
        titulo = f"{nombre} · {'VENDIDO' if vendido else cop(e.get('precio'))}"
        desc = " · ".join(x for x in [f"Lote {lote}", e.get("cat", ""), e.get("uso", ""), "Barranquilla"] if x)
        desc += ". YELLOW YARD by Nestor Sierra · Tu próxima máquina está en el patio amarillo."
        img = SITIO + (e.get("img") or "og.jpg")
        url = f"{SITIO}e/{lote}/"
        destino = f"../../#lote-{lote}"
        h = html.escape
        pagina = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{h(titulo)} · Yellow Yard</title>
<meta name="description" content="{h(desc)}">
<meta name="robots" content="noindex">
<link rel="canonical" href="{SITIO}#lote-{lote}">
<meta property="og:type" content="product">
<meta property="og:site_name" content="YELLOW YARD by Nestor Sierra">
<meta property="og:title" content="{h(titulo)}">
<meta property="og:description" content="{h(desc)}">
<meta property="og:image" content="{h(img)}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<meta http-equiv="refresh" content="0; url={destino}">
<script>location.replace("{destino}");</script>
<style>body{{margin:0;background:#0D0D0D;color:#ECE8DE;font-family:Georgia,serif;display:grid;place-items:center;min-height:100vh}}a{{color:#FFC20E}}</style>
</head><body><p>Abriendo la ficha del equipo… <a href="{destino}">Ver {h(nombre)}</a></p></body></html>
"""
        os.makedirs(os.path.join(base, lote), exist_ok=True)
        open(os.path.join(base, lote, "index.html"), "w", encoding="utf-8").write(pagina)
    print(f"fichas para compartir: {len(d['E'])}")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
