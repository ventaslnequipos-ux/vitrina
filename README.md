# Yellow Yard · Archivos fuente

Esta rama (`fuente`) guarda los archivos de trabajo del catálogo. La página pública vive en la rama `main` y se publica en https://ventaslnequipos-ux.github.io/vitrina/.

## Qué hay aquí

| Carpeta | Contenido |
|---|---|
| `web/vitrina.html` | **Fuente de los datos**: `const EQUIPOS = [...]`, `INGRESOS` (fecha de ingreso por equipo) y `FIJOS` (destacados fijos). De aquí sale `equipos.js`. |
| `web/patio.html` | Copia de `index.html` de la página principal (diseño Yellow Yard). |
| `tools/publicar.py` | **Publica el control privado en la página**: genera `equipos.js`, fotos con marca de agua y videos. |
| `web/marketplace.html` | Página de apoyo (noindex) con textos listos para publicar en Facebook Marketplace. |
| `tools/build_site.sh` | Genera `site/equipos.js` (desde vitrina.html) y `site/index.html` (desde patio.html). |
| `tools/marca_agua.py` | Pone la marca de agua (placa + "by Nestor Sierra") a las fotos: lee `img_limpias/*.jpg` y escribe `site/img/*.jpg`. |
| `tools/grabar3.py`, `frames3.py` | Graban la intro animada (brandout/anim3.html) a MP4 cuadrado y vertical. |
| `brandout/` | Piezas gráficas en HTML: intro animada, imagen para compartir (og2), QR, calcomanías, marca de agua, perfil. |
| `control/control.html` | Página privada de control (artifact de Claude con base de datos y banco de fotos). |
| `apps_script/Interesados.gs` | Script de Google para que el formulario "Me interesa" escriba en la hoja Interesados y avise por correo. |

Las rutas de los scripts apuntan a una carpeta de trabajo (`S=...`). En una sesión nueva, cambia esa variable por la carpeta que uses.

## Cómo se publica (desde el 4 de noviembre de 2026)

La única fuente de datos es el **control privado** (artifact de Claude, `control/control.html`): equipos, precios, estado, características técnicas, fotos y videos. La página pública ya no tiene modo privado ni botones de Nestor.

1. Nestor edita en el control (agregar equipo, cambiar precio, marcar vendido, subir fotos o videos, cambiar características). El control muestra cuántos cambios hay sin publicar.
2. Toca **Publicar en la página**. El control llama a la tarea programada «Publicar Yellow Yard en la página» (solo se ejecuta a pedido) por el conector Claude Code Remote.
3. La tarea baja la base del control, corre `tools/publicar.py` (fotos con marca de agua, videos, `equipos.js`, `medios.json`), hace commit y push a `main`, actualiza la hoja "Base de datos Yellow Yard" y deja el resultado en `sistema/publicacion` del control. La página se ve actualizada 1 a 3 minutos después del push.

Reglas de `publicar.py`: sale todo equipo con "Publicado en la web" marcado y estado distinto de Retirado; el lote es fijo; Vendido va a `VENDIDOS` (sello, sin precio, al final); la primera foto del banco es la principal; las fotos marcadas "Solo interno" no salen; `medios.json` guarda qué archivo del banco corresponde a cada foto o video ya publicado.

`web/vitrina.html` y `tools/build_site.sh` quedan como respaldo histórico: `equipos.js` ya no se genera desde ahí.

## Tipografía y colores

- Títulos: Alfa Slab One. Texto: Zilla Slab. Datos: IBM Plex Mono.
- Negro #0D0D0D / #161616 · Amarillo #FFC20E · Oro #C9A227 · Plata #BFC5CC.
- Las fuentes para renderizar localmente se bajan con un clon parcial de github.com/google/fonts (`ofl/alfaslabone`, `ofl/zillaslab`).
