"""
Applies a perfect flat-top hexagon mask + dark border to an image.
Flat-top = flat edges at top and bottom, points on left and right.
Uses 4x supersampling for smooth antialiased edges.

Usage:
    py scripts/hex_mask.py <image.png>         # overwrites in place
    py scripts/hex_mask.py <image.png> <out>   # saves to different file
    py scripts/hex_mask.py                     # runs on all Hex *.png in imgs/hexs/
"""
import sys
import math
import glob
import os
from PIL import Image, ImageDraw, ImageChops, ImageOps, ImageFilter

BORDER_WIDTH = 65  # pixels of dark border inset from hex edge

def make_hex_mask(w, h, r, scale):
    W, H = w * scale, h * scale
    CX, CY = w * scale / 2, h * scale / 2
    R = r * scale
    verts = [
        (CX + R * math.cos(math.radians(60 * i)),
         CY + R * math.sin(math.radians(60 * i)))
        for i in range(6)
    ]
    m = Image.new('L', (W, H), 0)
    ImageDraw.Draw(m).polygon(verts, fill=255)
    return m.resize((w, h), Image.LANCZOS)

def apply_hex_mask(input_path, output_path=None):
    if output_path is None:
        output_path = input_path

    img = Image.open(input_path).convert('RGBA')
    w, h = img.size
    r = min(w, h) / 2

    scale = 4

    # Outer hex mask (clip shape)
    mask_outer = make_hex_mask(w, h, r, scale)

    # Inner hex mask (defines where border starts)
    mask_inner = make_hex_mask(w, h, r - BORDER_WIDTH, scale)

    # Blur inner mask to create soft gradient toward the edge
    mask_inner_soft = mask_inner.filter(ImageFilter.GaussianBlur(radius=BORDER_WIDTH // 2))

    # Border alpha = inside hex AND NOT inside inner soft zone
    border_alpha = ImageChops.multiply(mask_outer, ImageOps.invert(mask_inner_soft))

    # Apply hex shape as alpha
    img.putalpha(mask_outer)

    # Build black border overlay and composite on top
    border_overlay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    border_overlay.putalpha(border_alpha)
    result = Image.alpha_composite(img, border_overlay)

    result.save(output_path, 'PNG')
    print(f'  OK: {os.path.basename(output_path)}')

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        apply_hex_mask(sys.argv[1], sys.argv[2] if len(sys.argv) >= 3 else None)
    else:
        # Default: all Hex *.png in imgs/hexs/ relative to project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        folder = os.path.join(project_root, 'imgs', 'hexs')
        images = glob.glob(os.path.join(folder, 'Hex *.png'))
        print(f'Processing {len(images)} images in {folder}...')
        for path in sorted(images):
            apply_hex_mask(path)
        print('Done.')
