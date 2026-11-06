"""Publica en la página pública lo que Nestor tiene en el control privado.

El control privado (artifact de Claude) guarda cada equipo en su base de datos (colección `equipos`)
y sus fotos y videos en el banco de archivos. Este script toma una copia de esa base y arma la
página pública (rama `main`): equipos.js, fotos con marca de agua y videos.

Pasos (los corre la tarea "Publicar Yellow Yard"):
  1. Bajar la base:   ArtifactData list equipos  -> <db>/equipos/*.json
  2. python3 publicar.py faltantes --db <db> --site <main>
        -> imprime los id de fotos/videos que todavía no están en la página (uno por línea)
  3. Bajar cada uno:  Artifact read path=<id>  -> copiarlo a <medios>/<id>.<ext>
  4. python3 publicar.py generar --db <db> --site <main> --medios <medios>
        -> reescribe equipos.js, agrega img/… y vid/…, actualiza medios.json y escribe
           <db>/informe.json con el resumen y los cambios que hay que devolver al control.

Reglas:
  - Sale en la página todo equipo con "Publicado en la web" marcado y estado distinto de "Retirado".
  - El número de lote es el del control y no cambia aunque se quiten equipos.
  - Estado "Vendido" -> VENDIDOS (sello, sin precio, al final). Cualquier otro estado -> disponible.
  - Fotos: la primera foto del banco es la principal. Solo salen las que no están marcadas
    "Solo interno" (campo publica = false). Llevan marca de agua y máximo 1100 px.
  - Videos: se copian tal cual (máximo 20 MB, el límite del banco).
  - Bajó de precio: si el precio publicado baja frente al que tenía la página, se guarda el anterior en
    PRECIO_ANTES (se muestra tachado con la chapa "Bajó de precio" durante 30 días; si el precio sube, se quita).
  - Combos: los equipos del control con el mismo campo combo.id salen juntos en COMBOS con su precio especial,
    solo si todos están publicados y disponibles.
  - Si un equipo del control no tiene "Características técnicas", se conservan las que ya
    tenía la página y se informan para guardarlas en el control.
"""
import argparse, datetime, json, os, re, glob, shutil, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
MARCA = os.path.join(AQUI, "..", "brandout", "marca.png")


def leer_js(site):
    src = open(os.path.join(site, "equipos.js"), encoding="utf-8").read()
    datos = json.loads(subprocess.check_output(["node", "-e", """
const fs=require('fs');const s=fs.readFileSync(process.argv[1],'utf8');
const f=new Function(s+';return {EQUIPOS, INGRESOS: typeof INGRESOS!=="undefined"?INGRESOS:{}, FIJOS: typeof FIJOS!=="undefined"?FIJOS:[], DESTACADO: typeof DESTACADO!=="undefined"?DESTACADO:"", PRECIO_ANTES: typeof PRECIO_ANTES!=="undefined"?PRECIO_ANTES:{}};');
process.stdout.write(JSON.stringify(f()));""", os.path.join(site, "equipos.js")]))
    for i, e in enumerate(datos["EQUIPOS"]):
        e.setdefault("lote", str(i + 1).zfill(2))
    return src, datos


def leer_db(db):
    filas = []
    for f in glob.glob(os.path.join(db, "equipos", "*.json")):
        d = json.load(open(f, encoding="utf-8"))
        d["_id"] = os.path.splitext(os.path.basename(f))[0]
        filas.append(d)
    return filas


def num(v):
    s = re.sub(r"[^\d]", "", str(v if v is not None else ""))
    return int(s) if s else 0


def lote_de(r):
    n = num(r.get("lote"))
    return str(n).zfill(2) if n else ""


def publicable(r):
    return r.get("web") is not False and r.get("estado") != "Retirado" and (r.get("nombre") or "").strip() and lote_de(r)


def medios_web(r):
    return [m for m in (r.get("media") or []) if m.get("publica") is not False and m.get("id")]


def cargar_mapa(site):
    p = os.path.join(site, "medios.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def specs_de(texto):
    out = []
    for linea in str(texto or "").splitlines():
        linea = linea.strip().lstrip("-•▪ ").strip()
        if not linea:
            continue
        k, sep, v = linea.partition(":")
        out.append([k.strip(), v.strip()] if sep and v.strip() else ["Dato", linea])
    return out


def marca_agua(origen, destino):
    from PIL import Image, ImageOps
    im = ImageOps.exif_transpose(Image.open(origen)).convert("RGB")
    im.thumbnail((1100, 1100), Image.LANCZOS)
    w, h = im.size
    marca = Image.open(MARCA).convert("RGBA")
    mw = max(130, int(min(w, h * 1.2) * 0.20))
    mk = marca.resize((mw, int(marca.height * mw / marca.width)), Image.LANCZOS)
    mk.putalpha(mk.split()[3].point(lambda v: int(v * 0.95)))
    m = int(min(w, h) * 0.025)
    im.paste(mk, (w - mk.width - m, h - mk.height - m), mk)
    im.save(destino, "JPEG", quality=86, optimize=True)


def js(v):
    return json.dumps(v, ensure_ascii=False)


def faltantes(a):
    mapa = cargar_mapa(a.site)
    for r in leer_db(a.db):
        if not publicable(r):
            continue
        for m in medios_web(r):
            if m["id"] not in mapa:
                print(m["id"])


def generar(a):
    src, viejo = leer_js(a.site)
    por_lote = {e["lote"]: e for e in viejo["EQUIPOS"]}
    mapa = cargar_mapa(a.site)
    os.makedirs(os.path.join(a.site, "img"), exist_ok=True)
    os.makedirs(os.path.join(a.site, "vid"), exist_ok=True)
    informe = {"publicados": 0, "vendidos": [], "fotos_nuevas": 0, "videos_nuevos": 0, "sin_archivo": [], "specs_sembrar": {}, "avisos": []}
    filas = sorted([r for r in leer_db(a.db) if publicable(r)], key=lambda r: num(r.get("lote")))
    vistos, equipos, vendidos, ingresos = set(), [], {}, {}
    for r in filas:
        l = lote_de(r)
        if l in vistos:
            informe["avisos"].append(f"Lote {l} repetido en el control: se publicó solo el primero.")
            continue
        vistos.add(l)
        ant = por_lote.get(l, {})
        fotos, videos = [], []
        for m in medios_web(r):
            ruta = mapa.get(m["id"])
            if not ruta:
                archivos = glob.glob(os.path.join(a.medios or "", m["id"] + ".*")) if a.medios else []
                if not archivos:
                    informe["sin_archivo"].append(f"lote {l}: {m.get('nombre') or m['id']}")
                    continue
                if m.get("tipo") == "video":
                    ext = os.path.splitext(archivos[0])[1].lower() or ".mp4"
                    ruta = f"vid/l{l}-{m['id'][:8]}{ext}"
                    shutil.copyfile(archivos[0], os.path.join(a.site, ruta))
                    informe["videos_nuevos"] += 1
                else:
                    ruta = f"img/l{l}-{m['id'][:8]}.jpg"
                    marca_agua(archivos[0], os.path.join(a.site, ruta))
                    informe["fotos_nuevas"] += 1
                mapa[m["id"]] = ruta
            (videos if m.get("tipo") == "video" else fotos).append(ruta)
        if not fotos and ant.get("img"):
            fotos = [ant["img"]]
        specs = specs_de(r.get("specs"))
        if not specs and ant.get("specs"):
            specs = ant["specs"]
            informe["specs_sembrar"][r["_id"]] = "\n".join(f"{k}: {v}" for k, v in specs)
        anio = r.get("anio")
        anio = num(anio) if num(anio) else 0
        e = {"lote": l, "img": fotos[0] if fotos else "", "tipo": r.get("tipo") or ant.get("tipo") or "Otros",
             "cat": r.get("cat") or ant.get("cat") or "", "nombre": r["nombre"].strip(), "anio": anio,
             "uso": r.get("uso") or "Por confirmar", "precio": num(r.get("precio_publicado")), "specs": specs}
        if len(fotos) > 1:
            e["fotos"] = fotos[1:]
        if videos:
            e["videos"] = videos
        equipos.append(e)
        if r.get("estado") == "Vendido":
            vendidos[e["nombre"]] = r.get("fecha_venta") or r.get("web_vendido") or ""
            informe["vendidos"].append(r["_id"])
        ing = r.get("fecha_ingreso") or viejo["INGRESOS"].get(e["nombre"]) or ""
        if ing:
            ingresos[e["nombre"]] = ing
    # Bajó de precio: precio anterior tachado durante 30 días
    hoy = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-5))).date()
    antes = {}
    for e in equipos:
        l, p = e["lote"], e["precio"]
        if e["nombre"] in vendidos or not p:
            continue
        reg = viejo["PRECIO_ANTES"].get(l)
        previo = por_lote.get(l, {}).get("precio", 0)
        if reg and reg.get("antes", 0) > p and (hoy - datetime.date.fromisoformat(reg.get("desde", str(hoy)))).days <= 30:
            antes[l] = reg
        elif previo and p < previo:
            antes[l] = {"antes": previo, "desde": str(hoy)}
    informe["bajaron"] = sorted(antes)
    # Combos: equipos con el mismo combo.id, todos publicados y disponibles
    grupos = {}
    for r in filas:
        c = r.get("combo") or {}
        if isinstance(c, dict) and c.get("id") and num(c.get("precio")):
            grupos.setdefault(c["id"], c)
    disponibles = {e["lote"] for e in equipos if e["nombre"] not in vendidos}
    combos = []
    for cid, c in grupos.items():
        lotes = [str(num(x)).zfill(2) for x in c.get("lotes", [])]
        if len(lotes) > 1 and all(x in disponibles for x in lotes):
            combos.append({"id": cid, "nombre": c.get("nombre", ""), "lotes": lotes, "precio": num(c["precio"])})
        else:
            informe["avisos"].append(f"Combo {cid} no se publicó: algún lote no está disponible en la página.")
    informe["combos"] = [c["id"] for c in combos]
    informe["publicados"] = len(equipos)
    nombres = {e["nombre"] for e in equipos}

    lineas = ["const EQUIPOS = ["]
    for e in equipos:
        cab = ", ".join(f"{k}: {js(e[k])}" for k in ["lote", "img", "tipo", "cat", "nombre", "anio", "uso", "precio"])
        extra = "".join(f", {k}: {js(e[k])}" for k in ["fotos", "videos"] if k in e)
        lineas.append(f"  {{ {cab}{extra},\n    specs: {js(e['specs'])} }},")
    lineas.append("];")
    lineas.append('// Fecha de ingreso al catálogo: la etiqueta "Nuevo ingreso" se muestra 15 días y luego se quita sola.')
    lineas.append("const INGRESOS = {")
    lineas += [f"  {js(k)}: {js(v)}," for k, v in ingresos.items()]
    lineas.append("};")
    lineas.append('// Equipos vendidos: nombre del equipo y fecha de venta. Siguen en el catálogo con el sello "Equipo vendido", al final de la lista,')
    lineas.append('// sin precio y fuera de destacados, cinta y "Nuevo ingreso". Se marcan desde el control privado (estado "Vendido").')
    lineas.append("const VENDIDOS = {")
    lineas += [f"  {js(k)}: {js(v)}," for k, v in vendidos.items()]
    lineas.append("};")
    lineas.append('// Precio anterior de los equipos que bajaron de precio (se muestra tachado 30 días). Lo calcula publicar.py.')
    lineas.append(f"const PRECIO_ANTES = {js(antes)};")
    lineas.append('// Combos: varios lotes juntos con precio especial. Se arman en el control privado (campo combo).')
    lineas.append(f"const COMBOS = {js(combos)};")
    lineas.append("// Carrusel de destacados: rota solo cada lunes (mínimo 3 o el 10 % del total). Si un equipo debe quedar fijo, poner su nombre aquí.")
    lineas.append(f"const FIJOS = {js([n for n in viejo['FIJOS'] if n in nombres])};")
    lineas.append("// Equipo destacado de la semana (cambiar el nombre para rotarlo).")
    dest = viejo["DESTACADO"] if viejo["DESTACADO"] in nombres and viejo["DESTACADO"] not in vendidos else next((e["nombre"] for e in equipos if e["nombre"] not in vendidos and e["img"] and e["precio"]), "")
    lineas.append(f"const DESTACADO = {js(dest)};")
    nuevo = "// Generado desde el control privado de Yellow Yard (tools/publicar.py en la rama fuente). No editar a mano.\n" + "\n".join(lineas) + "\n"
    open(os.path.join(a.site, "equipos.js"), "w", encoding="utf-8").write(nuevo)
    json.dump(mapa, open(os.path.join(a.site, "medios.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    subprocess.check_call(["node", "-e", "new Function(require('fs').readFileSync(process.argv[1],'utf8'))", os.path.join(a.site, "equipos.js")])
    # Página corta por equipo (e/<lote>/): el enlace compartido muestra la foto del equipo en WhatsApp
    subprocess.check_call([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "fichas_compartir.py"), a.site])
    json.dump(informe, open(os.path.join(a.db, "informe.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(informe, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("accion", choices=["faltantes", "generar"])
    p.add_argument("--db", required=True)
    p.add_argument("--site", required=True)
    p.add_argument("--medios")
    a = p.parse_args()
    (faltantes if a.accion == "faltantes" else generar)(a)
