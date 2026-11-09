"""Imagen para compartir (1200 x 630): placa nueva, YELLOW blanco + YARD ocre, bulldozer D6N de marca de agua, base de hierba fina."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

S = os.path.dirname(os.path.abspath(__file__)) + "/"
V = sys.argv[2] if len(sys.argv) > 2 else "../vitrina/"
OUT = sys.argv[1]
W, H = 1200, 630
OCRE = np.array([210, 155, 50]); NEGRO = np.array([13, 13, 13]); HUESO = np.array([240, 236, 226])
ORO = np.array([201, 162, 39])

lienzo = np.zeros((H, W, 3), float); lienzo[:] = NEGRO

# 1. Bulldozer de marca de agua (sin logos de marca, en tonos ocre)
foto = Image.open(V + "img/d6n17_hd.jpg").convert("RGB")
d = ImageDraw.Draw(foto)
for caja in [(500, 178, 556, 212), (985, 272, 1045, 318), (905, 240, 975, 266), (700, 182, 750, 208)]:  # logos CAT, placa y rótulo
    zona = foto.crop(caja).filter(ImageFilter.GaussianBlur(12))
    zona = Image.new("RGB", zona.size, tuple(int(v) for v in np.array(zona).reshape(-1, 3).mean(0)))
    foto.paste(zona, caja[:2])
foto = ImageOps.mirror(foto.crop((40, 20, 1600, 737)))  # la cuchilla queda mirando a la derecha
ESC = 0.74
g = np.array(ImageOps.autocontrast(foto.convert("L"), cutoff=1), float) / 255
ancho, alto = int(foto.width * ESC), int(foto.height * ESC)
g = np.array(Image.fromarray((g * 255).astype("uint8")).resize((ancho, alto), Image.LANCZOS), float) / 255
# máquina en la foto espejada (recortada): x ~ 475-1500, y ~ 50-600
mx0, mx1, my0, my1 = 475 * ESC, 1500 * ESC, 50 * ESC, 600 * ESC
x0 = int(1215 - mx1); y0 = int(596 - my1)
tinte = NEGRO + (OCRE * 1.08 - NEGRO) * (g[..., None] ** 1.1)
yy, xx = np.mgrid[0:alto, 0:ancho]
cx, cy, rx, ry = (mx0 + mx1) / 2, (my0 + my1) / 2 + 20, (mx1 - mx0) / 2 * 1.05, (my1 - my0) / 2 * 1.08
r = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
op = 0.66 * np.clip((1.12 - r) / 0.8, 0, 1) ** 1.3 * (1 - 0.6 * g ** 2.2)
xs = xx + x0
op *= np.clip((xs - 330) / 220, 0, 1)
xa, xb = max(0, x0), min(W, x0 + ancho); ya, yb = max(0, y0), min(H, y0 + alto)
sub = lienzo[ya:yb, xa:xb]
t = tinte[ya - y0:yb - y0, xa - x0:xb - x0]; o = op[ya - y0:yb - y0, xa - x0:xb - x0, None]
lienzo[ya:yb, xa:xb] = sub * (1 - o) + t * o
# velo oscuro detrás del bloque de texto, para leer bien sobre la máquina
yy, xx = np.mgrid[0:H, 0:W]
velo = 0.55 * np.clip(1 - ((xx - 560) / 360) ** 2 - ((yy - 300) / 240) ** 2, 0, 1)
lienzo = lienzo * (1 - velo[..., None]) + NEGRO * velo[..., None]


def pegar(mascara, x, y, color):
    global lienzo
    h, w = mascara.shape
    zona = lienzo[y:y + h, x:x + w]
    lienzo[y:y + h, x:x + w] = zona * (1 - mascara[..., None]) + np.array(color) * mascara[..., None]


viejo = np.array(Image.open(S + "og_textos_fuente.jpg").convert("RGB"), float)
FONDO = 17


def mascara(caja, canal, tope, piso=30):
    x1, y1, x2, y2 = caja
    c = viejo[y1:y2, x1:x2, canal]
    return np.clip((c - piso) / (tope - piso), 0, 1)


K = 0.84
def esc(m):
    h, w = m.shape
    return np.array(Image.fromarray((m * 255).astype("uint8")).resize((round(w * K), round(h * K)), Image.LANCZOS), float) / 255


# 2. Placa (logo nuevo)
LW, LH = 212, 265
logo = Image.open(S + "logo.png").convert("RGBA").resize((LW, LH), Image.LANCZOS)
la = np.array(logo, float) / 255
lx, ly = 58, 168
zona = lienzo[ly:ly + LH, lx:lx + LW]
lienzo[ly:ly + LH, lx:lx + LW] = zona * (1 - la[..., 3:]) + la[..., :3] * 255 * la[..., 3:]

# 3. Textos (tipografías de marca tomadas de la pieza anterior), al 84 %
TX = 318
pegar(esc(mascara((386, 92, 885, 186), 2, 255)), TX, 150, [255, 255, 255])        # YELLOW blanco
pegar(esc(mascara((396, 194, 708, 286), 0, 255)), TX + 8, 236, OCRE)                # YARD ocre
pegar(esc(mascara((386, 312, 785, 356), 0, 201)), TX, 324, ORO + 20)                # — by Nestor Sierra
sl = viejo[372:412, 384:1072]
bl = np.clip((sl[..., 2] - 30) / (238 - 30), 0, 1)
am = np.clip(np.clip((sl[..., 0] - 30) / (255 - 30), 0, 1) - bl, 0, 1)
pegar(esc(bl), TX, 377, HUESO - 6)
pegar(esc(am), TX, 377, OCRE + 14)

# 4. Botón de WhatsApp en ocre
img = Image.fromarray(lienzo.clip(0, 255).astype("uint8"))
dr = ImageDraw.Draw(img)
wa = viejo[443:486, 412:1032]
mw = esc(np.clip((194 - wa[..., 1]) / (194 - 18), 0, 1))
bx, by, bh = TX, 430, 54
bw = mw.shape[1] + 44
dr.rounded_rectangle((bx, by, bx + bw, by + bh), radius=bh // 2, fill=tuple(OCRE))
lienzo = np.array(img, float)
pegar(mw, bx + 22, by + (bh - mw.shape[0]) // 2 + 1, [20, 16, 10])

# 5. Base de hierba fina: filete ocre con tres matas
img = Image.fromarray(lienzo.clip(0, 255).astype("uint8"))
dr = ImageDraw.Draw(img)
yb = 598
dr.line((40, yb, W - 40, yb), fill=tuple(OCRE), width=3)
for cx in (W * 0.22, W * 0.5, W * 0.78):
    for x1, x2, alto in ((-14, -20, 22), (0, 3, 36), (14, 24, 20)):
        dr.line((cx + x1, yb, cx + x2, yb - alto), fill=tuple(OCRE), width=4)
        dr.ellipse((cx + x2 - 2, yb - alto - 2, cx + x2 + 2, yb - alto + 2), fill=tuple(OCRE))
# filete fino arriba, en oro
dr.line((0, 6, W, 6), fill=(120, 92, 32), width=2)
img.save(OUT, quality=88, optimize=True, progressive=True)
print("ok", OUT)
