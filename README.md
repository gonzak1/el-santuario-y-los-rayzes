# El Santuario y los Rayzes

Proyecto de juego de mesa con cartas y mapa hexagonal, diseñado para importar en Tabletop Simulator.

---

## Estructura

```
imgs/
  mazos/          # Cartas individuales organizadas por mazo (bosque, claro, montaña, río, ruinas, iniciales)
    <mazo>/       # PNGs de cada carta + subcarpeta back/ con el reverso
  sheets/         # Sheets generadas (una por mazo) — se importan en Tabletop Simulator
  hexs/           # Tiles hexagonales del mapa (Hex Bosque, Claro, etc.)
    back/         # Reverso del hexágono
scripts/
  hex_mask.py     # Script Python para dar forma hexagonal a los tiles
urls/
  import_tabletop.txt  # URLs y configuración para importar en Tabletop Simulator
```

---

## Aplicación C# — Generador de sheets

Lee las cartas en `imgs/mazos/<mazo>/` y genera una sheet (grilla de imágenes) por mazo en `imgs/sheets/`, lista para importar en Tabletop Simulator.

**Requisitos:** .NET 10

**Ejecutar:**
```bash
dotnet run
```

La grilla se arma con 3 columnas. La sheet resultante se sube al repositorio y se referencia desde `urls/import_tabletop.txt`.

---

## Script Python — Máscara hexagonal (`scripts/hex_mask.py`)

Aplica una máscara de hexágono perfecto (flat-top) con borde negro degradado a los tiles de `imgs/hexs/`. Usa supersampling 4x para bordes suavizados.

**Requisitos:** Python 3 + Pillow
```bash
pip install Pillow
```

**Uso:**
```bash
# Procesar una imagen específica (sobreescribe)
py scripts/hex_mask.py "imgs/hexs/Hex Bosque.png"

# Procesar todas las imágenes Hex *.png de una vez
py scripts/hex_mask.py
```

El grosor del borde se ajusta con la constante `BORDER_WIDTH` al inicio del script (default: 65 px).

---

## Importar en Tabletop Simulator

Las URLs y configuración de cada mazo y hexágono están en `urls/import_tabletop.txt`.
