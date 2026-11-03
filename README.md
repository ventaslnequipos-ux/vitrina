# Yellow Yard · Archivos fuente

Esta rama (`fuente`) guarda los archivos de trabajo del catálogo. La página pública vive en la rama `main` y se publica en https://ventaslnequipos-ux.github.io/vitrina/.

## Qué hay aquí

| Carpeta | Contenido |
|---|---|
| `web/vitrina.html` | **Fuente de los datos**: `const EQUIPOS = [...]`, `INGRESOS` (fecha de ingreso por equipo) y `FIJOS` (destacados fijos). De aquí sale `equipos.js`. |
| `web/patio.html` | **Plantilla de la página principal** (diseño Yellow Yard). Se copia tal cual a `index.html`. |
| `web/marketplace.html` | Página de apoyo (noindex) con textos listos para publicar en Facebook Marketplace. |
| `tools/build_site.sh` | Genera `site/equipos.js` (desde vitrina.html) y `site/index.html` (desde patio.html). |
| `tools/marca_agua.py` | Pone la marca de agua (placa + "by Nestor Sierra") a las fotos: lee `img_limpias/*.jpg` y escribe `site/img/*.jpg`. |
| `tools/grabar3.py`, `frames3.py` | Graban la intro animada (brandout/anim3.html) a MP4 cuadrado y vertical. |
| `brandout/` | Piezas gráficas en HTML: intro animada, imagen para compartir (og2), QR, calcomanías, marca de agua, perfil. |
| `control/control.html` | Página privada de control (artifact de Claude con base de datos y banco de fotos). |
| `apps_script/Interesados.gs` | Script de Google para que el formulario "Me interesa" escriba en la hoja Interesados y avise por correo. |

Las rutas de los scripts apuntan a una carpeta de trabajo (`S=...`). En una sesión nueva, cambia esa variable por la carpeta que uses.

## Agregar un equipo

1. Foto limpia (sin logos de otras empresas) en `img_limpias/<nombre>.jpg`, máximo 1100 px.
2. `python3 tools/marca_agua.py <nombre>.jpg` → crea `site/img/<nombre>.jpg` con marca de agua.
3. Agregar el objeto en `EQUIPOS` de `web/vitrina.html` y su fecha en `INGRESOS`.
4. `bash tools/build_site.sh`, copiar `site/index.html`, `site/equipos.js` y la foto a la rama `main`, commit y push.

## Marcar un equipo como vendido

1. Nestor abre la ficha del equipo en el control privado y toca **Marcar como vendido** (queda `estado: "Vendido"` y `fecha_venta`). "Deshacer venta" lo devuelve a Disponible.
2. El control muestra arriba los cambios "Por publicar en la página": son los equipos cuyo `estado` no coincide con `web_vendido`.
3. Al pedir «publica los vendidos», Claude lee la colección `equipos` del control, actualiza `VENDIDOS` en `web/vitrina.html` (nombre exacto del equipo: fecha de venta), corre `tools/build_site.sh`, copia `equipos.js` a `main`, hace commit y push, pone `web_vendido` (fecha) en el control (o lo borra si se deshizo la venta) y cambia el estado en la hoja "Base de datos Yellow Yard".
4. En la página el equipo queda con el sello "Equipo vendido · Yellow Yard by Nestor Sierra" en la esquina de la foto, sin precio, al final de la lista y fuera de destacados, cinta, "Nuevo ingreso" y "Mi consulta". La página de Marketplace avisa que hay que retirar esa publicación.

## Tipografía y colores

- Títulos: Alfa Slab One. Texto: Zilla Slab. Datos: IBM Plex Mono.
- Negro #0D0D0D / #161616 · Amarillo #FFC20E · Oro #C9A227 · Plata #BFC5CC.
- Las fuentes para renderizar localmente se bajan con un clon parcial de github.com/google/fonts (`ofl/alfaslabone`, `ofl/zillaslab`).
