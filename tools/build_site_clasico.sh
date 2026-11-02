#!/bin/bash
# Arma site/index.html (sitio público en GitHub Pages) a partir de web/vitrina.html
set -e
S=/tmp/claude-0/-home-claude/80e7857f-008c-5260-b5ef-714e7d23e49b/scratchpad
URL="https://ventaslnequipos-ux.github.io/vitrina/"
DESC="Tu próxima máquina está en el patio amarillo. Maquinaria y vehículos usados en venta, verificables en Barranquilla. WhatsApp 301 795 9540."
{
cat <<EOF
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="$DESC">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Yellow Yard">
<meta property="og:title" content="Yellow Yard · Tu próxima máquina está en el patio amarillo">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<meta property="og:description" content="$DESC">
<meta property="og:url" content="$URL">
<meta property="og:image" content="${URL}og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="es_CO">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="${URL}og.jpg">
<link rel="canonical" href="$URL">
EOF
sed -n '1,/^<\/style>/p' $S/web/vitrina.html
printf '</head>\n<body>\n'
sed -n '/^<\/style>/,$p' $S/web/vitrina.html | tail -n +2
printf '</body>\n</html>\n'
} > $S/site/index.html
sed -n '/^const EQUIPOS = \[/,/^const DESTACADO/p' $S/web/vitrina.html > $S/site/equipos.js
echo "site/index.html y equipos.js listos"
