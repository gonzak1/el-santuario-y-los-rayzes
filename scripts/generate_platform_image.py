"""
Genera la imagen de la plataforma de "supply" (mazos, hexágonos de repuesto,
bolsas) que se apoya sobre el borde de la mesa, por afuera del paño.

Tilea la textura "Wood Planks" (CC0, Poly Haven: https://polyhaven.com/a/wood_planks)
guardada en imgs/board/source/wood_planks_diff_2k.jpg para cubrir el tamaño
final de la plataforma.

Uso: py scripts/generate_platform_image.py
Salida: imgs/board/plataforma.png

El aspect ratio de esta imagen (WIDTH_PX : DEPTH_PX) no necesita coincidir con
la escala real de la plataforma en TTS: el Custom_Tile usa Stretch=True, así
que estira la imagen al tamaño que definan PLATFORM_SCALE_X / PLATFORM_SCALE_Z
en scripts/generate_tts_save.py.
"""
import os
from PIL import Image

WIDTH_PX  = 2048
DEPTH_PX  = 1024
TILE_PX   = 1024   # tamaño de cada repetición de la textura sobre el canvas

base_dir   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
source_path = os.path.join(base_dir, "imgs", "board", "source", "wood_planks_diff_2k.jpg")
out_dir    = os.path.join(base_dir, "imgs", "board")
os.makedirs(out_dir, exist_ok=True)
out_path   = os.path.join(out_dir, "plataforma.png")

tile = Image.open(source_path).convert("RGBA").resize((TILE_PX, TILE_PX), Image.LANCZOS)

canvas = Image.new("RGBA", (WIDTH_PX, DEPTH_PX))
for y in range(0, DEPTH_PX, TILE_PX):
    for x in range(0, WIDTH_PX, TILE_PX):
        canvas.paste(tile, (x, y))

canvas.save(out_path)
print(f"Generado: {out_path} ({WIDTH_PX}x{DEPTH_PX})")
