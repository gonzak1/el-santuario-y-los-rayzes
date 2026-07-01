"""
Genera la imagen de la plataforma de "supply" (mazos, hexágonos de repuesto,
bolsas) que se apoya sobre el borde de la mesa, por afuera del paño.

Uso: py scripts/generate_platform_image.py
Salida: imgs/board/plataforma.png

El aspect ratio de esta imagen (WIDTH_PX : DEPTH_PX) debe coincidir con
PLATFORM_WIDTH / PLATFORM_DEPTH en scripts/generate_tts_save.py, porque el
Custom_Tile usa WidthScale=0.0 (toma el ancho real de la imagen).
"""
import os
from PIL import Image, ImageDraw

WIDTH_PX  = 2048
DEPTH_PX  = 1024

WOOD_COLOR   = (92, 58, 33, 255)     # marrón madera, mismo tono que las bolsas
BORDER_COLOR = (61, 38, 21, 255)     # borde más oscuro para dar profundidad
BORDER_PX    = 24

out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "imgs", "board")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "plataforma.png")

img = Image.new("RGBA", (WIDTH_PX, DEPTH_PX), WOOD_COLOR)
draw = ImageDraw.Draw(img)
draw.rectangle([0, 0, WIDTH_PX - 1, DEPTH_PX - 1], outline=BORDER_COLOR, width=BORDER_PX)

img.save(out_path)
print(f"Generado: {out_path} ({WIDTH_PX}x{DEPTH_PX})")
