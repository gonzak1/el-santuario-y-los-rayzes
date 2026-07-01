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
  sombras/        # Tiles de sombra (Sombra 1, 2, 3)
  tokens/         # Tokens de Vida / Vida perdida
  board/          # Imagen de la plataforma de "supply" (plataforma.png)
scripts/
  hex_mask.py               # Script Python para dar forma hexagonal a los tiles
  generate_platform_image.py # Script Python que genera imgs/board/plataforma.png
  generate_tts_save.py      # Script Python que genera el save file de Tabletop Simulator
urls/
  import_tabletop.txt  # URLs y configuración para importar en Tabletop Simulator
El Santuario y los Rayzes.json  # Save file de Tabletop Simulator generado por generate_tts_save.py
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

## Script Python — Imagen de la plataforma (`scripts/generate_platform_image.py`)

Genera `imgs/board/plataforma.png`, una imagen lisa color madera usada como textura de la "plataforma de supply" (ver sección siguiente). El aspect ratio de esta imagen tiene que coincidir con `PLATFORM_WIDTH` / `PLATFORM_DEPTH` de `generate_tts_save.py`.

**Requisitos:** Python 3 + Pillow

**Uso:**
```bash
py scripts/generate_platform_image.py
```

---

## Script Python — Generador del save de Tabletop Simulator (`scripts/generate_tts_save.py`)

Genera `El Santuario y los Rayzes.json`, el save file completo de Tabletop Simulator: mazos de cartas, hexágonos de terreno, bolsas de sombras, token de Vida y la bolsa "Generar Mapa" (con el script Lua que arma el mapa hexagonal aleatorio al hacer clic en el botón dentro de TTS).

Todo ese "supply" (mazos, hexágonos de repuesto, bolsas) se apoya sobre una **plataforma** (`Custom_Tile` rectangular) corrida hacia afuera de la mesa, dejando el paño completamente libre para el mapa generado (que sigue apareciendo centrado en el paño, sin cambios). La posición/tamaño de la plataforma se controla con estas constantes al inicio del script — son de ajuste manual, hay que probarlas en TTS e ir afinando:

- `PLATFORM_Z_SHIFT`: cuánto se corre el supply en Z hacia afuera de la mesa.
- `PLATFORM_Y_LIFT`: cuánto se levanta el supply para que apoye sobre la plataforma sin atravesarla.
- `PLATFORM_WIDTH` / `PLATFORM_DEPTH`: tamaño real (en unidades TTS) de la plataforma. Deben mantener el mismo aspect ratio que `imgs/board/plataforma.png`.
- `PLATFORM_SCALE`: escala del `Custom_Tile` de la plataforma.

Todas las URLs de imágenes apuntan al repo en GitHub (`raw.githubusercontent.com`), por lo que hay que subir los cambios de `imgs/` antes de regenerar o usar el save.

**Requisitos:** Python 3 (sin dependencias externas)

**Uso:**
```bash
py scripts/generate_tts_save.py
```

**Salida:** `El Santuario y los Rayzes.json` en la raíz del repo.

Copiar el archivo generado a `Documentos/My Games/Tabletop Simulator/Saves/` y cargarlo desde TTS en `Games > Load > El Santuario y los Rayzes`.

---

## Importar en Tabletop Simulator

Las URLs y configuración de cada mazo y hexágono están en `urls/import_tabletop.txt`.
