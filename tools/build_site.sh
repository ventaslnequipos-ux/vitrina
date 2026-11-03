#!/bin/bash
# Arma el sitio público (GitHub Pages).
# - Los datos de los equipos siguen en web/vitrina.html (const EQUIPOS ... DESTACADO) -> site/equipos.js
# - La página principal es web/patio.html (diseño Yellow Yard by Nestor Sierra) -> site/index.html
set -e
S=${S:-$(cd "$(dirname "$0")/.." && pwd)}   # carpeta de trabajo (por defecto, la raíz de esta rama)
mkdir -p $S/site
sed -n '/^const EQUIPOS = \[/,/^const DESTACADO =/p' $S/web/vitrina.html > $S/site/equipos.js
cp $S/web/patio.html $S/site/index.html
cp $S/web/marketplace.html $S/site/marketplace.html
cat > $S/site/v2.html <<'R'
<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=./"><link rel="canonical" href="./"><title>Yellow Yard</title><a href="./">Ir al catálogo Yellow Yard</a>
R
echo "site/index.html y equipos.js listos"
